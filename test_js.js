/**
 * test_js.js — Research Suite Pure JS 测试运行器
 * 运行所有核心算法，无需任何依赖
 */
'use strict';

// ═══════ MATH ═══════
function normalCDF(z){return 0.5*(1+erf(Math.abs(z)/Math.sqrt(2)));}
function erf(x){const a=[.254829592,-.284496736,1.421413741,-1.453152027,1.061405429,.3275911];const s=x<0?-1:1;x=Math.abs(x);const t=1/(1+a[5]*x);const y=1-((((((a[4]*t+a[3])*t)+a[2])*t+a[1])*t+a[0])*t*Math.exp(-x*x));return s*y;}
function gammaLn(x){const c=[76.18009172947146,-86.50532032941677,24.01409824083091,-1.231739572450155,.001208650973866179,-.000005395239384953];let y=x,t=x+5.5;t-=(x+.5)*Math.log(t);let s=1.000000000190015;for(let j=0;j<6;j++)s+=c[j]/++y;return -t+Math.log(2.5066282746310005*s/x);}
function regBeta(z,a,b){if(z===0||z===1)return z;const bt=Math.exp(gammaLn(a+b)-gammaLn(a)-gammaLn(b)+a*Math.log(z)+b*Math.log(1-z));return z<(a+1)/(a+b+2)?bt*betaCF(z,a,b)/a:1-bt*betaCF(1-z,b,a)/b;}
function betaCF(z,a,b){const M=200,E=1e-10;let c=1,d=1-(a+b)*z/(a+1);d=Math.abs(d)<1e-30?1e-30:1/d;let h=d;for(let m=1;m<M;m++){const m2=2*m,aa=m*(b-m)*z/((a+m2-1)*(a+m2));d=1+aa*d;c=1+aa/(Math.abs(c)<1e-30?1e-30:c);d=1/d;h*=d*c;aa=-(a+m)*(a+b+m)*z/((a+m2)*(a+m2+1));d=1+aa*d;c=1+aa/(Math.abs(c)<1e-30?1e-30:c);d=1/d;const del=d*c;h*=del;if(Math.abs(del-1)<E)break;}return h;}
function chi2CDF(x,df){if(df<=0||x<0)return x>=0?1:0;if(df>100){const z=(Math.pow(x/df,1/3)-(1-2/(9*df)))/Math.sqrt(2/(9*df));return normalCDF(z);}return 1-regBeta(df/(df+x),df/2,.5);}

// ═══════ PICO ═══════
class PICOExtractor{extract(t){const F=p=>{const o=[];for(const r of p){const g=new RegExp(r,'gi');let m;while((m=g.exec(t))!==null)o.push((m[1]||m[0]).trim());}return[...new Set(o)].filter(x=>x.length>3).slice(0,5);};const pop=F([`population[s]?[:\\s]+([^\\.]+)`]),int_=F([`treated with ([\\w\\s]{3,30})`]),comp=F([`versus ([\\w\\s]{3,20})`]),out=F([`efficacy|safety|mortality|response rate`]);const st=[];if(/randomized|rct|randomised/.test(t))st.push('RCT');if(/cohort|prospective/.test(t))st.push('队列研究');return{population:pop,intervention:int_,comparison:comp,outcome:out,study_type:[...new Set(st)].slice(0,3)};}}

// ═══════ RoB2 ═══════
class RoB2Assessor{assessText(t,title='Unknown'){const f=k=>t.includes(k);const R=f('randomized')||f('rct')?'Low':(f('quasi-random')?'High':'Unknown');const A=f('allocation concealment')||f('sealed envelope')?'Low':(f('open-label')?'High':'Unknown');const BP=f('double-blind')?'Low':(f('open-label')?'High':'Unknown');const BO=f('double-blind')||f('independent')?'Low':(f('open-label')?'High':'Unknown');const Att=!f('dropout')&&!f('lost to follow')?'Low':(f('intention-to-treat')?'Low':'Some concerns');const Rep=f('clinicaltrials.gov')||f('registration')?'Low':'Some concerns';const O=f('funded by')?'Some concerns':'Unknown';const con=['Some concerns','High'].filter(x=>[R,A,BP,BO,Att,Rep,O].includes(x)).length;const Ov=con===0?'Low':con<=2?'Some concerns':'High';return{paper_title:title,randomization:R,allocation:A,blinding_participants:BP,blinding_outcome:BO,attrition:Att,reporting:Rep,other:O,overall:Ov};}}

// ═══════ GRADE ═══════
class GRADEAssessor{assess(outcome,studyDesign='RCT',kwargs={}){let s=studyDesign==='RCT'?4:2;for(const k of['risk_of_bias','inconsistency','indirectness','imprecision','publication_bias'])if(kwargs[k])s--;if(studyDesign!=='RCT')s+=['dose_response','large_magnitude','confounders'].filter(k=>kwargs[k]).length;s=Math.max(0,Math.min(5,s));const m={5:'High',4:'High',3:'Moderate',2:'Low',1:'Very Low',0:'Very Low'};return{outcome,study_design:studyDesign,quality:m[s]||'Unknown'};}}

// ═══════ JBI ═══════
class JBIAssessor{assess(t,studyType='RCT',title='Unknown'){const isRCT=/randomized|rct/.test(t);let score=0;if(isRCT){if(/randomized|randomised/.test(t))score++;if(/allocation concealment|sealed/.test(t))score++;if(/double-blind|blinded/.test(t))score++;if(/placebo|control/.test(t))score++;score++;if(/intention-to-treat|multivariate/.test(t))score++;}const maxS=isRCT?10:8;return{study_type:studyType,paper_title:title,score,max_score:maxS,qualityLabel:()=>(score/maxS>=.8?'✅高质量':score/maxS>=.5?'⚠️中等':'❌低质量')};}}

// ═══════ EVIDENCE TABLE ═══════
class EvidenceTableGenerator{generate(papers,format='markdown'){if(!papers||!papers.length)return'**无相关文献**';const rows=papers.map(p=>({name:`${(p.authors||['?'])[0]} et al. (${p.year||'N/A'})`,year:p.year||'N/A',journal:p.journal||'N/A',source:p.source||'N/A',doi:p.doi||'N/R'}));if(format==='csv')return['Study,Year,Journal,Source,DOI',...rows.map(r=>`"${r.name}",${r.year},"${r.journal}",${r.source},${r.doi}`)].join('\n');let md=`# 证据表格 (共${rows.length}项)\n\n| Study | Year | Journal | Source |\n|-------|------|---------|--------|\n`;return md+rows.map(r=>`| ${r.name} | ${r.year} | ${r.journal} | ${r.source} |`).join('\n');}}

// ═══════ PRISMA ═══════
class PRISMAGenerator{generateManual(o={}){const d={dbRecords:o.dbRecords||0,duplicates:o.duplicates||0,afterDedup:0,query:o.query||'',databases:o.databases||[],date:new Date().toISOString().split('T')[0]};d.afterDedup=d.dbRecords-d.duplicates;d.assessed=o.assessed||0;d.excluded=o.excluded||0;d.includedReports=o.includedReports||0;return d;}toAsciiDiagram(d){return`\n╔══════════════════════════════════════════════════════╗\n║  IDENTIFICATION                                    ║\n╠══════════════════════════════════════════════════════╣\n║  数据库=${d.dbRecords} 去重后=${d.afterDedup}                   ║\n╠══════════════════════════════════════════════════════╣\n║  全文评估=${d.assessed} 排除=${d.excluded}                         ║\n╠══════════════════════════════════════════════════════╣\n║  ✅纳入=${d.includedReports} 检索词=${d.query.substring(0,30)}         ║\n╚══════════════════════════════════════════════════════╝`;}}

// ═══════ IMRAD ═══════
class IMRADWriter{generate(topic,papers=[],sections=['background','methods','results']){const today=new Date().toISOString().split('T')[0];let o=`# ${topic}\n\n*自动生成 · ${papers.length}篇 · ${today}*\n\n`;if(sections.includes('background'))o+=`## 1.引言\n\n${topic}是当前研究热点。本综述检索${papers.length}篇文献。\n\n### 研究Gap\n1.样本量偏小\n2.随访数据不足\n3.亚组不一致\n\n`;if(sections.includes('methods'))o+=`## 2.方法\n\n数据库：PubMed/arXiv/Semantic Scholar\n检索词：${topic}\n质量评估：RoB2/ROBINS-I/GRADE\n\n`;if(sections.includes('results')){o+=`## 3.结果\n\n共${papers.length}篇，纳入${Math.min(papers.length,10)}篇全文评估：\n\n`;papers.slice(0,5).forEach((p,i)=>{o+=`${i+1}. ${p.title||'N/A'} — ${(p.authors||[]).join(', ')}(${p.year||'N/A'})\n`;});}return o+'\n';}}

// ═══════ REF FORMATTER ═══════
class ReferenceFormatter{constructor(s='bibtex'){this.s=s;}format(papers){return papers.map(p=>{const a=(p.authors||[]).join(' and '),y=p.year||'n.d.',t=p.title||'Untitled',j=p.journal||'',d=p.doi||'';if(this.s==='bibtex'){const k=((p.authors||['X'])[0].split(' ').pop()+y).replace(/[^a-zA-Z0-9]/g,'');return`@article{${k},\n  title = {${t}},\n  author = {${a}},\n  journal = {${j}},\n  year = {${y}},\n  doi = {${d}},\n}`;}if(this.s==='vancouver'){const au=(p.authors||[]).length>6?(p.authors||[]).slice(0,3).map(a=>a.split(' ').pop()).join(', ')+', et al.':(p.authors||[]).map(a=>a.split(' ').pop()).join(', ');return`${au}. ${t}. ${j}. ${y}.`;}if(this.s==='ris'){let o='TY  - JOUR\n';(p.authors||[]).forEach(a=>o+=`AU  - ${a}\n`);return o+`TI  - ${t}\nJO  - ${j}\nPY  - ${y}\nDO  - ${d}\nER  -\n`;}return'';}).join('\n');}}

// ═══════ EFFECT SIZE ═══════
class EffectSizeExtractor{extractAll(text){const results=[];const patterns=[{type:'RR',pat:/RR\s*=\s*([0-9.]+)/gi},{type:'OR',pat:/\bOR\s*=\s*([0-9.]+)/gi},{type:'HR',pat:/\bHR\s*=\s*([0-9.]+)/gi}];for(const {type,pat} of patterns){let m;while((m=pat.exec(text))!==null){const v=parseFloat(m[1]);if(!v||v<=0)continue;const ci=/95%\s*CI[:\s]+([0-9.]+)\s*[-–to]+\s*([0-9.]+)/i.exec(text.substring(m.index,m.index+200));const pv=/p\s*[=<>]\s*([0-9.]+)/.exec(text.substring(m.index-30,m.index+100));const cl=ci?parseFloat(ci[1]):null,cu=ci?parseFloat(ci[2]):null,pVal=pv?parseFloat(pv[1]):null;results.push({type,point_estimate:v,ci_lower:cl,ci_upper:cu,p_value:pVal,significant:pVal!==null&&pVal<.05,ln_rr:type==='RR'||type==='OR'||type==='HR'?Math.log(v):v});}}return results;}}

// ═══════ HETEROGENEITY ═══════
class HeterogeneityCalculator{calculate(effects){const n=effects.length;const lns=effects.map(e=>e.ln_rr||0);const vs=effects.map(e=>{if(e.ci_lower!==undefined&&e.ci_upper!==undefined&&e.ci_lower>0)return Math.pow((Math.log(e.ci_upper)-Math.log(e.ci_lower))/(2*1.96),2);return e.variance||1;});const ws=vs.map(v=>1/Math.max(v,1e-6));const sumW=ws.reduce((a,b)=>a+b,0);const pooled=ws.reduce((s,w,i)=>s+w*lns[i],0)/sumW;const Q=ws.reduce((s,w,i)=>s+w*Math.pow(lns[i]-pooled,2),0);const df=n-1;const pV=1-chi2CDF(Q,df);const iSq=Q>0?Math.max(0,(Q-df)/Q*100):0;const tauSq=Q>df?Math.max(0,(Q-df)/(sumW-ws.reduce((s,w)=>s+w*w,0)/sumW)):0;const normW=ws.map(w=>w/sumW*100);return{n_studies:n,q_statistic:Q,df,p_value:pV,i_squared:iSq,tau_squared:tauSq,i2_label:iSq<25?'低':iSq<50?'中度':iSq<75?'较高':'高',rec:pV<.1||iSq>50?'🔴建议随机效应':'🟢可用固定效应',weights:normW};}}

// ═══════ FOREST PLOT ═══════
class ForestPlotGenerator{generate(studies,pooled,het,model='random',et='RR'){const fmt=(v)=>(et==='RR'||et==='OR'||et==='HR'?Math.exp(v):v).toFixed(2);const nW=20;let o=`\n╔══════════════════════════════════════════════════════════╗\n║  森林图 — ${et}                                    ║\n╚══════════════════════════════════════════════════════════╝\n${'研究'.padEnd(nW)}  ${'效应量'.padEnd(8)}  ${'95%CI'.padEnd(18)}  ${'权重'}\n${'─'.repeat(nW+32)}\n${'[汇总]'.padEnd(nW)}  ${fmt(pooled.effect).padEnd(8)}  ${fmt(pooled.ci_lower)}–${fmt(pooled.ci_upper).padEnd(15)}  100%\n${'─'.repeat(nW+32)}\n`;for(const s of studies){const lnE=Math.log(Math.max(s.effect,.001)),lnL=Math.log(Math.max(s.ci_lower,.001)),lnU=Math.log(Math.max(s.ci_upper,.001));o+=`${(s.name+' '+s.year).substring(0,nW).padEnd(nW)}  ${fmt(lnE).padEnd(8)}  ${fmt(lnL)}–${fmt(lnU).padEnd(15)}  ${s.weight.toFixed(1)}%\n`;}o+=`\n无效线=1.00 I²=${(het.i2||0).toFixed(1)}% Q=${(het.q||0).toFixed(2)}\n`;return o;}}

// ═══════ META ANALYZER ═══════
class MetaAnalyzer{constructor(){this._s=[];}addStudyDirect(name,type,effect,ciL,ciU,year=null){const lnE=type==='RR'||type==='OR'||type==='HR'?Math.log(Math.max(effect,.001)):effect;const lnL=ciL>0?Math.log(ciL):ciL,lnU=Math.log(Math.max(ciU,.001));const se=(lnU-lnL)/(2*1.96);this._s.push({name,year,type,ciL,ciU,lnE,lnL,lnU,var:se*se});}analyze(model=null){if(this._s.length<2)return{error:'需要至少2项研究'};const calc=new HeterogeneityCalculator();const het=calc.calculate(this._s.map(s=>({ln_rr:s.lnE,ci_lower:s.lnL,ci_upper:s.lnU})));if(!model)model=het.p_value<.1||het.i_squared>50?'random':'fixed';const ws=this._s.map(s=>1/Math.max(s.var,1e-6));const sumW=ws.reduce((a,b)=>a+b,0);let lnP=ws.reduce((a,w,i)=>a+w*this._s[i].lnE,0)/sumW;if(model==='random'){const tSq=het.tau_squared;const adjW=this._s.map(s=>1/Math.max(s.var+tSq,1e-6));const sumWA=adjW.reduce((a,b)=>a+b,0);lnP=adjW.reduce((a,w,i)=>a+w*this._s[i].lnE,0)/sumWA;}const pSE=Math.sqrt(1/sumW),lnCL=lnP-1.96*pSE,lnCU=lnP+1.96*pSE;const z=lnP/pSE,pVal=2*(1-normalCDF(Math.abs(z)));const et=this._s[0]?.type||'RR';const toR=v=>et==='RR'||et==='OR'||et==='HR'?Math.exp(v):v;const nW=ws.map(w=>w/sumW*100);this._s.forEach((s,i)=>s.wPct=nW[i]);return{n_studies:this._s.length,model,effect_type:et,pooled:{effect:toR(lnP),ci_lower:toR(lnCL),ci_upper:toR(lnCU),pvalue:pVal,significant:pVal<.05},heterogeneity:{q:Number(het.q_statistic.toFixed(3)),df:het.df,p:Number(het.p_value.toFixed(4)),i2:Number(het.i_squared.toFixed(1)),label:het.i2_label,rec:het.rec},studies:this._s.map(s=>({name:s.name,year:s.year,effect:s.ciL,ci:`[${s.ciL},${s.ciU}]`,weight:Number((s.wPct||0).toFixed(1)),p:s.pVal})),toReport(){let o=`╔══════════════════════════════════════════════════════╗\n║  🔬Meta分析结果                                  ║\n╚══════════════════════════════════════════════════════╝\n\n`;o+=`📊${this.n_studies}项 | ${this.model==='random'?'随机':'固定'}效应 | ${this.effect_type}\n`;o+=`📈 合并${this.effect_type}=${this.pooled.effect.toFixed(3)}(95%CI:${this.pooled.ci_lower.toFixed(3)}–${this.pooled.ci_upper.toFixed(3)}) p=${this.pooled.pvalue.toFixed(4)}\n`;o+=`📐 I²=${this.heterogeneity.i2}% Q=${this.heterogeneity.q} p=${this.heterogeneity.p} — ${this.heterogeneity.label}\n\n`;o+=`${this.studies.map(s=>`  ${s.name.padEnd(20)} ${s.year||'? '} ${s.effect.toFixed(3)}(${s.ci}) w=${s.weight}%`).join('\n')}\n`;return o;};}}

// ═══════ ENTITY EXTRACTOR ═══════
class EntityExtractor{extractEntities(text){const r=[],s=new Set();const d={gene:['TP53','BRCA1','BRCA2','EGFR','KRAS','MYC','PTEN','HER2','PD-1','PD-L1','CTLA-4','VEGF','IL-6','STAT3','AKT','mTOR','PI3K','MAPK','ERK','BRAF','BCL-2','CD8','CD4'],disease:['cancer','tumor','carcinoma','melanoma','lymphoma','leukemia','diabetes','obesity','hypertension','cardiovascular','stroke','Alzheimer','Parkinson','depression','arthritis','asthma'],drug:['aspirin','metformin','insulin','atorvastatin','paclitaxel','cisplatin','doxorubicin','trastuzumab','pembrolizumab','nivolumab','ipilimumab','dexamethasone','rapamycin','imatinib','rituximab'],pathway:['PI3K/AKT','mTOR','MAPK','ERK','JAK/STAT','NF-κB','WNT','HIF','AMPK','Apoptosis','PD-1/PD-L1','CTLA-4'],symptom:['fatigue','pain','fever','inflammation','edema','headache','nausea','vomiting','dyspnea','anemia','anxiety']};for(const[type,terms]of Object.entries(d)){for(const term of terms){if(new RegExp('\\b'+term.replace('-','\\-')+'\\b','i').test(text)){const id=`${type}:${term.toUpperCase()}`;if(!s.has(id)){s.add(id);r.push({id,name:term,type});}}}}return r;}}

// ═══════ TEST RUNNER ═══════
let passed=0,failed=0;
function test(name,fn){
    process.stdout.write(`\n${'═'.repeat(60)}\nTEST: ${name}\n`);
    try{fn();process.stdout.write(`  ✅ PASS\n`);passed++;}
    catch(e){process.stdout.write(`  ❌ FAIL: ${e.message}\n`);failed++;}
}
function eq(a,b,msg=''){if(JSON.stringify(a)!==JSON.stringify(b))throw new Error(`${msg||'assert'} — expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);}
function ok(v,msg=''){if(!v)throw new Error(msg||'expected truthy');}

// TESTS
test('PICO Extractor',()=>{
    const e=new PICOExtractor();
    const r=e.extract('Aspirin for cardiovascular disease prevention in adults');
    ok(r.intervention.length>0||r.population.length>0,'should extract');
    process.stdout.write(`  P:${r.population.length} I:${r.intervention.length} O:${r.outcome.length}\n`);
});

test('RoB 2 — Good RCT',()=>{
    const a=new RoB2Assessor();
    const r=a.assessText('This was a randomized, double-blind, placebo-controlled trial. Randomization was adequate. Allocation concealed. Intention-to-treat analysis. Registered at ClinicalTrials.gov.','Good RCT');
    process.stdout.write(`  Overall: ${r.overall}\n`);
    ok(['Low','Some concerns','High'].includes(r.overall),'overall valid');
    process.stdout.write(`  ${r.overall}\n`);
});

test('GRADE — RCT降一级',()=>{
    const a=new GRADEAssessor();
    const r=a.assess('Mortality','RCT',{risk_of_bias:false,inconsistency:true,indirectness:false,imprecision:false,publication_bias:false});
    process.stdout.write(`  Quality: ${r.quality}\n`);
    ok(['High','Moderate','Low','Very Low'].includes(r.quality),'quality valid');
    eq(r.quality,'Moderate','RCT-1降级=Moderate');
});

test('JBI — RCT paper',()=>{
    const a=new JBIAssessor();
    const r=a.assess('Randomized trial. Allocation concealed. Double-blind. Placebo controlled. ITT analysis.','RCT','Test JBI');
    process.stdout.write(`  Score: ${r.score}/${r.max_score} — ${r.qualityLabel()}\n`);
    ok(r.score>=4,'should score at least 4');
});

test('Evidence Table',()=>{
    const g=new EvidenceTableGenerator();
    const papers=[{title:'Statins study',authors:['Smith A'],year:'2022',journal:'NEJM',doi:'10.1234/nejm'},{title:'Aspirin trial',authors:['Jones B'],year:'2021',journal:'Lancet',doi:'10.5678/lancet'}];
    const md=g.generate(papers,'markdown');
    ok(md.includes('Statins'),'should include title');
    ok(md.includes('NEJM'),'should include journal');
    process.stdout.write(`  ${md.split('\n').slice(0,4).join('\n  ')}\n`);
    const csv=g.generate(papers,'csv');
    ok(csv.includes('Smith'),'csv ok');
});

test('PRISMA Generator',()=>{
    const g=new PRISMAGenerator();
    const d=g.generateManual({dbRecords:1500,duplicates:450,assessed:250,includedReports:12,query:'Statins CV',databases:['pubmed','arxiv']});
    eq(d.afterDedup,1050);
    eq(d.includedReports,12);
    process.stdout.write(`  ${g.toAsciiDiagram(d)}\n`);
});

test('IMRAD Writer',()=>{
    const w=new IMRADWriter();
    const papers=[{title:'Statins outcomes',authors:['Smith A'],year:'2022',journal:'NEJM',doi:'10.1234'}];
    const r=w.generate('Statins for cardiovascular prevention',papers,['background','methods','results']);
    ok(r.includes('Statins'),'topic ok');
    ok(r.includes('引言'),'intro ok');
    ok(r.includes('方法'),'methods ok');
    ok(r.includes('结果'),'results ok');
    process.stdout.write(`  Generated ${r.length} chars\n`);
});

test('Reference Formatter',()=>{
    const papers=[{title:'Test study',authors:['Smith A','Jones B'],year:'2022',journal:'NEJM',doi:'10.1234/nejm'}];
    for(const s of ['bibtex','vancouver','ris']){
        const f=new ReferenceFormatter(s);
        const o=f.format(papers);
        ok(o.length>0,`${s} should output`);
        process.stdout.write(`  [${s}] ${o.substring(0,60).replace(/\n/g,' ')}...\n`);
    }
});

test('Effect Size Extractor',()=>{
    const e=new EffectSizeExtractor();
    const text='RR=0.75, 95%CI:0.55-1.02, p=0.06. OR was 0.68 (95%CI:0.50-0.92). HR=0.72 95%CI:0.55-0.95.';
    const r=e.extractAll(text);
    process.stdout.write(`  Found ${r.length} effect sizes:\n`);
    r.forEach(x=>process.stdout.write(`    - ${x.type}: ${x.point_estimate} [${x.ci_lower}–${x.ci_upper}] p=${x.p_value}\n`));
    eq(r.length,3,'should find 3');
    eq(r.find(x=>x.type==='RR')?.point_estimate,0.75,'RR=0.75');
    eq(r.find(x=>x.type==='OR')?.point_estimate,0.68,'OR=0.68');
    eq(r.find(x=>x.type==='HR')?.point_estimate,0.72,'HR=0.72');
});

test('Heterogeneity Calculator',()=>{
    const c=new HeterogeneityCalculator();
    const effects=[{ln_rr:-0.43,ci_lower:-0.73,ci_upper:-0.13},{ln_rr:-0.33,ci_lower:-0.60,ci_upper:-0.05},{ln_rr:-0.55,ci_lower:-0.92,ci_upper:-0.17},{ln_rr:-0.37,ci_lower:-0.69,ci_upper:-0.05}];
    const r=c.calculate(effects);
    process.stdout.write(`  Q=${r.q_statistic.toFixed(2)} I²=${r.i_squared.toFixed(1)}% p=${r.p_value.toFixed(4)}\n`);
    process.stdout.write(`  ${r.rec}\n`);
    ok(r.n_studies===4,'4 studies');
    ok(r.i_squared>=0&&r.i_squared<=100,'I² in range');
});

test('Forest Plot Generator',()=>{
    const g=new ForestPlotGenerator();
    const studies=[{name:'Smith',year:2020,effect:0.75,ci_lower:0.55,ci_upper:1.02,weight:25},{name:'Johnson',year:2021,effect:0.68,ci_lower:0.50,ci_upper:0.92,weight:30},{name:'Williams',year:2022,effect:0.82,ci_lower:0.60,ci_upper:1.12,weight:20},{name:'Brown',year:2023,effect:0.71,ci_lower:0.52,ci_upper:0.97,weight:25}];
    const o=g.generate(studies,{effect:0.72,ci_lower:0.60,ci_upper:0.87},{i2:20,q:2.5});
    ok(o.includes('森林图'),'includes header');
    ok(o.includes('Smith'),'includes Smith');
    ok(o.includes('Johnson'),'includes Johnson');
    process.stdout.write(o);
});

test('Meta Analyzer — Random Effects',()=>{
    const m=new MetaAnalyzer();
    m.addStudyDirect('Smith 2020','OR',0.65,0.48,0.88,2020);
    m.addStudyDirect('Johnson 2021','OR',0.72,0.55,0.95,2021);
    m.addStudyDirect('Williams 2022','OR',0.58,0.40,0.84,2022);
    m.addStudyDirect('Brown 2023','OR',0.69,0.50,0.95,2023);
    const r=m.analyze('random');
    process.stdout.write(`  ${r.toReport()}\n`);
    eq(r.n_studies,4,'4 studies');
    ok(r.pooled.effect>0&&r.pooled.effect<2,'effect valid');
    ok(r.heterogeneity.i2>=0,'I² non-negative');
    process.stdout.write(`  ✅ pooled OR=${r.pooled.effect.toFixed(3)} I²=${r.heterogeneity.i2}%\n`);
});

test('Meta Analyzer — Fixed Effects',()=>{
    const m=new MetaAnalyzer();
    m.addStudyDirect('Study1','RR',0.80,0.70,0.92,2020);
    m.addStudyDirect('Study2','RR',0.78,0.65,0.94,2021);
    const r=m.analyze('fixed');
    ok(r.model==='fixed','fixed model');
    eq(r.n_studies,2);
});

test('Entity Extractor',()=>{
    const e=new EntityExtractor();
    const text='TP53 mutations cause breast cancer. EGFR inhibitors treat lung cancer. PD-1 blockade activates T cells.';
    const r=e.extractEntities(text);
    process.stdout.write(`  ${r.length} entities:`);
    r.forEach(x=>process.stdout.write(` [${x.type}]${x.name}`));
    process.stdout.write('\n');
    ok(r.length>0,'should find entities');
    const types=r.map(x=>x.type);
    ok(types.includes('gene'),'gene found');
    ok(types.includes('disease'),'disease found');
});

// SUMMARY
process.stdout.write(`\n${'═'.repeat(60)}\n`);
process.stdout.write(`  📊 结果: ${passed} 通过, ${failed} 失败, 共 ${passed+failed} 项测试\n`);
process.stdout.write(`${'═'.repeat(60)}\n`);
if(failed===0){process.stdout.write(`  🎉 全部通过！\n`);}else{process.stdout.write(`  ⚠️  ${failed}项失败\n`);process.exit(1);}
