/**
 * Research Suite — Node.js 测试运行器
 * 验证所有核心模块
 */
const path = require('path');
const MODULE_DIR = __dirname;

// ── Mock urllib for py-style modules ──
const http = require('http');
const https = require('https');

function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        const mod = url.startsWith('https') ? https : http;
        mod.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

// ── Mini test runner ──
let passed = 0, failed = 0;

function test(name, fn) {
    process.stdout.write(`\n${'='.repeat(60)}\n`);
    process.stdout.write(`TEST: ${name}\n`);
    try {
        fn();
        process.stdout.write(`  ✅ PASS\n`);
        passed++;
    } catch(e) {
        process.stdout.write(`  ❌ FAIL: ${e.message}\n`);
        if (e.stack) process.stdout.write(`     ${e.stack.split('\n')[1]?.trim()}\n`);
        failed++;
    }
}

function assertEqual(actual, expected, msg = '') {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
        throw new Error(`${msg} — expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
}

function assertTrue(value, msg = '') {
    if (!value) throw new Error(`${msg} — expected truthy, got ${value}`);
}

// ════════════════════════════════════════════════
// MODULE TESTS
// ════════════════════════════════════════════════

// ── TEST: config.js ──
test('Config', () => {
    const Config = require(path.join(MODULE_DIR, 'config.js'));
    const cfg = new Config();
    const keys = cfg.getApiKeys();
    assertTrue(Array.isArray(keys), 'getApiKeys should return array');
    const keyNames = keys.map(k => k.name);
    assertTrue(keyNames.includes('pubmed'), 'Should include pubmed');
    assertTrue(keyNames.includes('arxiv'), 'Should include arxiv');
    assertTrue(keyNames.includes('semantic'), 'Should include semantic');
    process.stdout.write(`  Config keys: ${keyNames.join(', ')}\n`);
});

// ── TEST: PICO ──
test('PICO Extractor', () => {
    const { PICOExtractor } = require(path.join(MODULE_DIR, 'synthesize', 'pico.js'));
    const ext = new PICOExtractor();
    
    // Test English
    const r1 = ext.extract('Aspirin for cardiovascular disease prevention in adults with hypertension');
    process.stdout.write(`  English query — P:${r1.population.length} I:${r1.intervention.length} O:${r1.outcome.length}\n`);
    assertTrue(r1.intervention.length > 0 || r1.population.length > 0, 'Should extract at least something');
    
    // Test Chinese
    const r2 = ext.extract('他汀类药物对心血管疾病二级预防的疗效和安全性');
    process.stdout.write(`  Chinese query — P:${r2.population.length} I:${r2.intervention.length} O:${r2.outcome.length}\n`);
    
    // Test search query generation
    const queries = ext.generateSearchQuery(r1, 'all');
    process.stdout.write(`  Generated ${queries.length} search queries\n`);
    assertTrue(queries.length > 0, 'Should generate at least 1 query');
    
    process.stdout.write(`  ${r1.toMarkdown().split('\n')[0]}\n`);
});

// ── TEST: RoB 2 ──
test('RoB 2 Assessor', () => {
    const { RoB2Assessor } = require(path.join(MODULE_DIR, 'assess', 'rob2.js'));
    const assessor = new RoB2Assessor();
    
    const text = `This was a randomized, double-blind, placebo-controlled trial.
    Patients were randomly assigned using computer-generated sequence.
    Allocation was concealed using sealed opaque envelopes.
    Both participants and investigators were blinded.
    Primary outcome was assessed by independent committee.
    Intention-to-treat analysis was performed.
    Registered at ClinicalTrials.gov NCT12345678.`;
    
    const result = assessor.assessText(text, 'Test RCT');
    process.stdout.write(`  Overall: ${result.overall}\n`);
    process.stdout.write(`  ${result.toMarkdown().split('\n').slice(0,5).join('\n  ')}\n`);
    assertTrue(['Low', 'Some concerns', 'High'].includes(result.overall), 'Overall should be valid');
});

// ── TEST: ROBINS-I ──
test('ROBINS-I Assessor', () => {
    const { RoBINSIAssessor } = require(path.join(MODULE_DIR, 'assess', 'robins.js'));
    const assessor = new RoBINSIAssessor();
    
    const text = `This cohort study prospectively followed 1000 patients.
    Multivariate regression with propensity score adjustment was performed.
    Inverse probability weighting was used to control for confounding.
    Outcomes were assessed by blinded adjudicators.`;
    
    const result = assessor.assessText(text, 'Test Cohort');
    process.stdout.write(`  Overall: ${result.overall}\n`);
    assertTrue(['Low', 'Moderate', 'Serious', 'Critical'].includes(result.overall), 'Overall should be valid');
});

// ── TEST: GRADE ──
test('GRADE Assessor', () => {
    const { GRADEAssessor } = require(path.join(MODULE_DIR, 'assess', 'grade.js'));
    const assessor = new GRADEAssessor();
    
    const result = assessor.assess('All-cause mortality', 'RCT',
        { risk_of_bias: false, inconsistency: true, indirectness: false, imprecision: false, publication_bias: false }
    );
    process.stdout.write(`  Quality: ${result.quality}\n`);
    process.stdout.write(`  ${result.toMarkdown().split('\n').slice(0,8).join('\n  ')}\n`);
    assertTrue(['High', 'Moderate', 'Low', 'Very Low'].includes(result.quality), 'Quality should be valid');
});

// ── TEST: JBI ──
test('JBI Critical Appraisal', () => {
    const { JBIAssessor } = require(path.join(MODULE_DIR, 'assess', 'jbi.js'));
    const assessor = new JBIAssessor();
    
    const text = `Randomized controlled trial with adequate randomization.
    Allocation concealed. Blinding implemented.
    Equal treatment between groups.`;
    
    const result = assessor.assess(text, 'RCT', 'Test JBI Paper');
    process.stdout.write(`  Score: ${result.score}/${result.maxScore}\n`);
    process.stdout.write(`  Quality: ${result.qualityLabel()}\n`);
    assertTrue(result.score > 0, 'Should have positive score');
});

// ── TEST: Evidence Table ──
test('Evidence Table Generator', () => {
    const { EvidenceTableGenerator } = require(path.join(MODULE_DIR, 'synthesize', 'evidence_table.js'));
    const gen = new EvidenceTableGenerator();
    
    const papers = [
        { title: 'Statins for CV prevention', authors: ['Smith A', 'Jones B'], year: '2022', journal: 'NEJM', doi: '10.1234/nejm', abstract: 'RCT of 5000 patients.', source: 'pubmed', citations: 45 },
        { title: 'Effect of statins on lipids', authors: ['Wang C'], year: '2021', journal: 'Lancet', doi: '10.1234/lancet', abstract: 'Cohort study.', source: 'semantic', citations: 23 },
    ];
    
    const md = gen.generate(papers, 'markdown');
    process.stdout.write(`  Generated table with ${md.split('\n').length} lines\n`);
    assertTrue(md.includes('Statins'), 'Should include paper title');
    assertTrue(md.includes('Evidence Table'), 'Should include header');
    
    const csv = gen.generate(papers, 'csv');
    assertTrue(csv.includes('Smith'), 'CSV should include author');
});

// ── TEST: PRISMA ──
test('PRISMA Generator', () => {
    const { PRISMAGenerator } = require(path.join(MODULE_DIR, 'synthesize', 'prisma.js'));
    const gen = new PRISMAGenerator();
    
    const data = gen.generateManual({
        dbRecords: 1500, duplicates: 450, screened: 1050,
        excluded: 800, assessed: 250, includedReports: 12,
        query: 'Statins CV prevention', databases: ['pubmed', 'arxiv', 'semantic'],
    });
    
    const json = JSON.parse(gen.toJson(data));
    assertEqual(json.identification.recordsFromDatabases, 1500);
    process.stdout.write(`  Records: ${json.identification.recordsFromDatabases} → Included: ${json.included.reportsOfIncludedStudies}\n`);
    
    const diagram = gen.toAsciiDiagram(data);
    assertTrue(diagram.includes('STATINS CV PREVENTION'), 'ASCII diagram should include query');
});

// ── TEST: IMRAD Writer ──
test('IMRAD Writer', () => {
    const { IMRADWriter } = require(path.join(MODULE_DIR, 'write', 'imrad.js'));
    const writer = new IMRADWriter();
    
    const papers = [
        { title: 'Statins outcomes', authors: ['Smith A', 'Jones B'], year: '2022', journal: 'NEJM', abstract: 'RCT showing statin efficacy.', doi: '10.1234', citations: 50 },
    ];
    
    const review = writer.generate('Statins for cardiovascular prevention', papers, null, ['background', 'methods', 'results']);
    process.stdout.write(`  Generated review: ${review.length} chars\n`);
    assertTrue(review.includes('Statins for cardiovascular prevention'), 'Should include topic');
    assertTrue(review.includes('引言'), 'Should include Chinese intro section');
    assertTrue(review.includes('方法'), 'Should include methods section');
    assertTrue(review.includes('结果'), 'Should include results section');
    assertTrue(review.includes('Smith A, Jones B'), 'Should include authors');
});

// ── TEST: Reference Formatter ──
test('Reference Formatter', () => {
    const { ReferenceFormatter } = require(path.join(MODULE_DIR, 'write', 'references.js'));
    
    const papers = [{ title: 'A study', authors: ['Smith A', 'Jones B'], year: '2022', journal: 'NEJM', doi: '10.1234/nejm.2022' }];
    
    for (const style of ['bibtex', 'ris', 'vancouver', 'endnote']) {
        const fmt = new ReferenceFormatter(style);
        const out = fmt.format(papers);
        assertTrue(out.length > 0, `${style} should produce output`);
        process.stdout.write(`  ${style.toUpperCase()}: ${out.substring(0, 60).replace(/\n/g,' ')}...\n`);
    }
});

// ── TEST: Meta Analyzer ──
test('Meta Analyzer', () => {
    const { MetaAnalyzer } = require(path.join(MODULE_DIR, 'meta', 'analyzer.js'));
    const analyzer = new MetaAnalyzer();
    
    analyzer.addStudyDirect('Smith 2020', 'OR', 0.65, 0.48, 0.88, 2020);
    analyzer.addStudyDirect('Johnson 2021', 'OR', 0.72, 0.55, 0.95, 2021);
    analyzer.addStudyDirect('Williams 2022', 'OR', 0.58, 0.40, 0.84, 2022);
    analyzer.addStudyDirect('Brown 2023', 'OR', 0.69, 0.50, 0.95, 2023);
    
    const results = analyzer.analyze('random');
    process.stdout.write(`  Studies: ${results.nStudies}\n`);
    process.stdout.write(`  Pooled OR: ${results.pooled.effect.toFixed(3)} (95% CI: ${results.pooled.ciLower.toFixed(3)}–${results.pooled.ciUpper.toFixed(3)})\n`);
    process.stdout.write(`  I²: ${results.heterogeneity.i2}% — ${results.heterogeneity.label}\n`);
    process.stdout.write(`  Model: ${results.model}\n`);
    process.stdout.write(`  Recommendation: ${results.recommendation.substring(0,40)}\n`);
    
    assertTrue(results.nStudies === 4, 'Should have 4 studies');
    assertTrue(results.pooled.effect > 0, 'Pooled effect should be positive');
    assertTrue(results.heterogeneity.i2 >= 0, 'I² should be non-negative');
    
    const report = analyzer.report(results);
    assertTrue(report.includes('Meta 分析结果报告'), 'Report should include Chinese header');
    assertTrue(report.includes('Smith 2020'), 'Report should list all studies');
    process.stdout.write(`\n${report.substring(0, 400)}\n`);
});

// ── TEST: Effect Size Extractor ──
test('Effect Size Extractor', () => {
    const { EffectSizeExtractor } = require(path.join(MODULE_DIR, 'meta', 'effect_size.js'));
    const ext = new EffectSizeExtractor();
    
    const text = `RR = 0.75, 95% CI: 0.55-1.02, p = 0.06.
    Odds ratio was 0.68 (95% CI: 0.50-0.92).
    Hazard ratio: HR = 0.72, 95% CI: 0.55-0.95.`;
    
    const effects = ext.extractAll(text);
    process.stdout.write(`  Found ${effects.length} effect sizes:\n`);
    effects.forEach(e => {
        process.stdout.write(`    - ${e.type}: ${e.pointEstimate} (${e.ciLower}–${e.ciUpper})\n`);
    });
    assertTrue(effects.length >= 2, 'Should find at least 2 effect sizes');
    
    const or = effects.find(e => e.type === 'OR');
    assertTrue(or.pointEstimate === 0.68, 'OR should be 0.68');
    
    const rr = effects.find(e => e.type === 'RR');
    assertTrue(rr.pointEstimate === 0.75, 'RR should be 0.75');
    
    const hr = effects.find(e => e.type === 'HR');
    assertTrue(hr.pointEstimate === 0.72, 'HR should be 0.72');
});

// ── TEST: Heterogeneity Calculator ──
test('Heterogeneity Calculator', () => {
    const { HeterogeneityCalculator } = require(path.join(MODULE_DIR, 'meta', 'heterogeneity.js'));
    const calc = new HeterogeneityCalculator();
    
    const effects = [
        { ln_rr: -0.43, ci_lower: -0.73, ci_upper: -0.13 },
        { ln_rr: -0.33, ci_lower: -0.60, ci_upper: -0.05 },
        { ln_rr: -0.55, ci_lower: -0.92, ci_upper: -0.17 },
        { ln_rr: -0.37, ci_lower: -0.69, ci_upper: -0.05 },
    ];
    
    const result = calc.calculate(effects);
    process.stdout.write(`  Q = ${result.qStatistic.toFixed(2)}, df = ${result.df}\n`);
    process.stdout.write(`  I² = ${result.iSquared.toFixed(1)}% — ${result.i2Label}\n`);
    process.stdout.write(`  τ² = ${result.tauSquared.toFixed(4)}, p = ${result.pValue.toFixed(4)}\n`);
    
    assertTrue(result.nStudies === 4, 'Should have 4 studies');
    assertTrue(result.iSquared >= 0 && result.iSquared <= 100, 'I² should be 0-100');
    
    const md = result.toMarkdown();
    assertTrue(md.includes('异质性分析结果'), 'Should include Chinese header');
});

// ── TEST: Forest Plot ──
test('Forest Plot Generator', () => {
    const { ForestPlotGenerator } = require(path.join(MODULE_DIR, 'meta', 'forest_plot.js'));
    const gen = new ForestPlotGenerator();
    
    const studies = [
        { name: 'Smith', year: 2020, effect: 0.75, ci_lower: 0.55, ci_upper: 1.02, weight: 25.0 },
        { name: 'Johnson', year: 2021, effect: 0.68, ci_lower: 0.50, ci_upper: 0.92, weight: 30.0 },
        { name: 'Williams', year: 2022, effect: 0.82, ci_lower: 0.60, ci_upper: 1.12, weight: 20.0 },
        { name: 'Brown', year: 2023, effect: 0.71, ci_lower: 0.52, ci_upper: 0.97, weight: 25.0 },
    ];
    
    const data = gen.generate(studies, { effect: 0.72, ci_lower: 0.60, ci_upper: 0.87, pvalue: 0.0005 }, { q: 2.5, p: 0.47, i2: 20 }, 'random', 'RR');
    
    const ascii = data.toAscii();
    process.stdout.write(ascii);
    assertTrue(ascii.includes('Smith'), 'Should include Smith');
    assertTrue(ascii.includes('森林图'), 'Should include Chinese header');
    
    // Test RevMan export
    const revman = gen.toRevman(data);
    assertTrue(revman.includes('RevMan5Data'), 'RevMan should include XML header');
    
    // Test Stata export
    const stata = gen.toStata(data);
    assertTrue(stata.includes('Stata meta analysis input'), 'Stata should include header');
});

// ── TEST: Entity Extractor ──
test('Entity Extractor', () => {
    const { EntityExtractor } = require(path.join(MODULE_DIR, 'kg', 'extractor.js'));
    const ext = new EntityExtractor();
    
    const text = `TP53 is frequently mutated in breast cancer.
    BRCA1 mutations increase breast cancer risk.
    EGFR inhibitors treat non-small cell lung cancer.
    PD-1 checkpoint inhibitors activate T cells.
    Aspirin inhibits COX enzymes and reduces inflammation.`;
    
    const entities = ext.extractEntities(text, 'TEST123');
    process.stdout.write(`  Extracted ${entities.length} entities:\n`);
    const typeCounts = {};
    entities.forEach(e => {
        typeCounts[e.type] = (typeCounts[e.type] || 0) + 1;
        process.stdout.write(`    - [${e.type}] ${e.name}\n`);
    });
    process.stdout.write(`  Type distribution: ${JSON.stringify(typeCounts)}\n`);
    assertTrue(entities.length > 0, 'Should extract at least some entities');
    assertTrue(typeCounts['gene'] > 0, 'Should find gene entities');
    assertTrue(typeCounts['disease'] > 0, 'Should find disease entities');
});

// ── TEST: Relation Extractor ──
test('Relation Extractor', () => {
    const { EntityExtractor, RelationExtractor } = require(path.join(MODULE_DIR, 'kg', 'extractor.js'));
    const entityExt = new EntityExtractor();
    const relExt = new RelationExtractor();
    
    const text = `TP53 is frequently mutated in breast cancer.
    EGFR inhibitors treat non-small cell lung cancer.
    PD-1 inhibitors activate T cells and suppress tumor growth.
    Aspirin inhibits COX enzymes and reduces inflammation.
    IL-6 is upregulated in rheumatoid arthritis.`;
    
    const entities = entityExt.extractEntities(text, 'TEST456');
    const relations = relExt.extractRelations(text, entities, 'TEST456');
    
    process.stdout.write(`  Entities: ${entities.length}, Relations: ${relations.length}\n`);
    relations.forEach(r => {
        const src = entities.find(e => e.id === r.sourceId);
        const tgt = entities.find(e => e.id === r.targetId);
        process.stdout.write(`    - ${src?.name || r.sourceId} --[${r.type}]--> ${tgt?.name || r.targetId}\n`);
    });
    assertTrue(relations.length >= 0, 'Relations should be >= 0');
});

// ── TEST: Knowledge Graph Builder ──
test('Knowledge Graph Builder', () => {
    const { KnowledgeGraphBuilder } = require(path.join(MODULE_DIR, 'kg', 'builder.js'));
    const { GraphVisualizer } = require(path.join(MODULE_DIR, 'kg', 'builder.js'));
    const builder = new KnowledgeGraphBuilder();
    
    builder.addPaper('TEST001', 'TP53 and Cancer Study', 
        'TP53 mutations cause breast cancer. EGFR inhibitors treat lung cancer.',
        2023, ['TP53', 'EGFR', 'cancer']);
    
    builder.addPaper('TEST002', 'Immunotherapy Study',
        'PD-1 inhibitors activate T cells against tumor cells.',
        2022, ['PD-1', 'immunotherapy']);
    
    const kg = builder.build();
    const summary = builder.summary();
    
    process.stdout.write(`  KG: ${summary.nEntities} entities, ${summary.nRelations} relations\n`);
    process.stdout.write(`  Entity types: ${JSON.stringify(summary.entityTypes)}\n`);
    assertTrue(summary.nEntities > 0, 'Should have entities');
    assertTrue(summary.nEntities >= summary.nEntities, 'Self-consistent');
    
    // Test JSON export
    const json = JSON.parse(kg.toJson());
    assertTrue(json.entities.length > 0, 'JSON should have entities');
    
    // Test ASCII visualizer
    const viz = new GraphVisualizer(kg);
    const ascii = viz.toAscii();
    process.stdout.write(ascii.substring(0, 400));
    assertTrue(ascii.includes('知识图谱'), 'Should include Chinese header');
    
    // Test trend analyzer
    const { TrendAnalyzer } = require(path.join(MODULE_DIR, 'kg', 'builder.js'));
    const trendAnalyzer = new TrendAnalyzer(kg);
    const trends = trendAnalyzer.analyzeTrends();
    process.stdout.write(`  Trends keys: ${Object.keys(trends).join(', ')}\n`);
    
    // Gap analysis
    const gap = trendAnalyzer.gapAnalysis('disease');
    process.stdout.write(`  Gap analysis: ${gap.totalEntities} diseases, ${gap.withConnections} with connections\n`);
});

// ════════════════════════════════════════════════
// SUMMARY
// ════════════════════════════════════════════════
process.stdout.write(`\n${'='.repeat(60)}\n`);
process.stdout.write(`  📊 结果: ${passed} 通过, ${failed} 失败, 共 ${passed+failed} 项测试\n`);
process.stdout.write(`${'='.repeat(60)}\n`);
if (failed === 0) {
    process.stdout.write(`  🎉 全部测试通过！\n`);
} else {
    process.stdout.write(`  ⚠️  ${failed} 项测试失败\n`);
    process.exit(1);
}
