"""
森林图 (Forest Plot) 数据生成器
生成可导入可视化工具的森林图数据
支持: raw JSON / Plotly / matplotlib / RevMan format
"""
import json
import math
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ForestPlotStudy:
    """森林图单项研究数据"""
    name: str                  # 研究名称
    year: int                  # 年份
    effect: float              # 效应量 (log scale)
    ci_lower: float            # 95% CI 下限
    ci_upper: float            # 95% CI 上限
    weight: float              # 权重 (%)
    n_total: Optional[int] = None     # 总样本量
    n_events: Optional[int] = None     # 事件数
    group: str = ""            # 研究分组（亚组分析用）
    
    # 原始值（非 log，用于显示）
    effect_raw: Optional[float] = None
    ci_raw_lower: Optional[float] = None
    ci_raw_upper: Optional[float] = None


@dataclass
class ForestPlotData:
    """森林图完整数据"""
    studies: list[ForestPlotStudy]
    pooled_effect: float       # 合并效应量 (log)
    pooled_ci_lower: float
    pooled_ci_upper: float
    pooled_pvalue: float
    heterogeneity: dict         # 异质性统计
    model: str = "random"      # random / fixed
    effect_type: str = "RR"    # RR / OR / HR / RD
    summary_line: float = 0.0  # 无效线位置
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
    
    def to_plotly(self) -> dict:
        """生成 Plotly.js 森林图配置"""
        labels = []
        effects = []
        ci_lowers = []
        ci_uppers = []
        weights = []
        
        for s in self.studies:
            label = f"{s.name} ({s.year})"
            labels.append(label)
            effects.append(s.effect)
            ci_lowers.append(s.ci_lower)
            ci_uppers.append(s.ci_upper)
            weights.append(s.weight)
        
        # 添加汇总行
        labels.append(f"**汇总** {'(随机效应)' if self.model == 'random' else '(固定效应)'}")
        effects.append(self.pooled_effect)
        ci_lowers.append(self.pooled_ci_lower)
        ci_uppers.append(self.pooled_ci_upper)
        weights.append(100.0)
        
        # 转换为原始尺度用于显示
        if self.effect_type in ['RR', 'OR', 'HR']:
            display_effects = [math.exp(e) for e in effects]
            display_lowers = [math.exp(e) for e in ci_lowers]
            display_uppers = [math.exp(e) for e in ci_uppers]
        else:
            display_effects = effects
            display_lowers = ci_lowers
            display_uppers = ci_uppers
        
        return {
            'type': 'forest',
            'data': [{
                'name': label,
                'effect': eff,
                'ci_lower': cl,
                'ci_upper': cu,
                'weight': w,
                'display_effect': de,
                'display_ci_lower': dl,
                'display_ci_upper': du,
            } for label, eff, cl, cu, w, de, dl, du in zip(
                labels, effects, ci_lowers, ci_uppers, weights,
                display_effects, display_lowers, display_uppers
            )],
            'layout': {
                'title': f"森林图 — {self.effect_type}",
                'xaxis_title': f'{self.effect_type} (95% CI)',
                'shapes': [{
                    'type': 'line',
                    'x0': self.summary_line,
                    'x1': self.summary_line,
                    'y0': -0.5,
                    'y1': len(labels) - 0.5,
                    'line': {'color': 'red', 'width': 1.5, 'dash': 'dash'},
                }],
                'annotations': [{
                    'x': self.summary_line,
                    'y': len(labels),
                    'text': '无效线',
                    'showarrow': False,
                    'font': {'color': 'red'},
                }],
            },
            'heterogeneity': self.heterogeneity,
            'pooled': {
                'effect': self.pooled_effect,
                'ci_lower': self.pooled_ci_lower,
                'ci_upper': self.pooled_ci_upper,
                'pvalue': self.pooled_pvalue,
            }
        }
    
    def to_ascii(self) -> str:
        """生成纯 ASCII 艺术森林图"""
        def fmt(v):
            if self.effect_type in ['RR', 'OR', 'HR']:
                return f"{math.exp(v):.2f}"
            return f"{v:.3f}"
        
        lines = ["\n╔═══════════════════════════════════════════════════════════════════╗",
                 f"║             森林图 — {self.effect_type} (95% CI)                           ║",
                 "╚═══════════════════════════════════════════════════════════════════╝\n"]
        
        max_name_len = max(len(s.name) + 6 for s in self.studies)
        col_w = 8
        
        # 表头
        name_w = max(25, max_name_len)
        lines.append(f"{'':>{name_w}s}  {'效应量':>10s}  {'95% CI':>20s}  {'权重':>8s}")
        lines.append("─" * (name_w + 44))
        
        # 合并后（汇总）
        summary_eff = fmt(self.pooled_effect)
        summary_ci = f"{fmt(self.pooled_ci_lower)}–{fmt(self.pooled_ci_upper)}"
        lines.append(
            f"{'[汇总]':>{name_w}s}  "
            f"{summary_eff:>10s}  "
            f"{summary_ci:>20s}  "
            f"{'[100%]':>8s}"
        )
        
        lines.append("─" * (name_w + 44))
        
        # 各研究
        for s in self.studies:
            name = f"{s.name} ({s.year})"
            eff_str = fmt(s.effect)
            ci_str = f"{fmt(s.ci_lower)}–{fmt(s.ci_upper)}"
            w_str = f"{s.weight:.1f}%"
            lines.append(
                f"{name:>{name_w}s}  "
                f"{eff_str:>10s}  "
                f"{ci_str:>20s}  "
                f"{w_str:>8s}"
            )
        
        # 无效线
        null_line = " " * (name_w + 2)
        lines.append(f"\n无效线位置: {fmt(self.summary_line)} ({self.effect_type}=1.00 或 0.00)")
        
        # 异质性
        het = self.heterogeneity
        lines.append(f"\n异质性: I²={het.get('i2','N/A')}% | Q={het.get('q','N/A'):.2f} | p={het.get('p','N/A')}")
        
        return '\n'.join(lines)


class ForestPlotGenerator:
    """
    森林图数据生成器
    
    输入: 效应量列表 + 置信区间
    输出: 
    - JSON 格式（供 Plotly / D3 可视化）
    - ASCII 艺术图（终端预览）
    - RevMan 格式（导入 Cochrane RevMan）
    """
    
    def generate(
        self,
        studies: list[dict],
        pooled: dict,
        heterogeneity: dict,
        model: str = "random",
        effect_type: str = "RR",
    ) -> ForestPlotData:
        """
        生成森林图数据
        
        Args:
            studies: 研究列表，每个包含 name, year, effect, ci_lower, ci_upper, weight
            pooled: 汇总结果 {effect, ci_lower, ci_upper, pvalue}
            heterogeneity: 异质性统计
            model: 'random' 或 'fixed'
            effect_type: 'RR', 'OR', 'HR', 'MD', 'SMD'
        """
        plot_studies = []
        
        for s in studies:
            # log 转换（如果需要）
            if effect_type in ['RR', 'OR', 'HR']:
                ln_eff = math.log(s.get('effect', 1))
                ln_ci_low = math.log(max(s.get('ci_lower', 0.001), 0.001))
                ln_ci_high = math.log(s.get('ci_upper', 1))
            else:
                ln_eff = s.get('effect', 0)
                ln_ci_low = s.get('ci_lower', 0)
                ln_ci_high = s.get('ci_upper', 0)
            
            plot_studies.append(ForestPlotStudy(
                name=s.get('name', 'Unknown'),
                year=s.get('year', 0),
                effect=ln_eff,
                ci_lower=ln_ci_low,
                ci_upper=ln_ci_high,
                weight=s.get('weight', 0),
                n_total=s.get('n_total'),
                n_events=s.get('n_events'),
                group=s.get('group', ''),
                effect_raw=s.get('effect'),
                ci_raw_lower=s.get('ci_lower'),
                ci_raw_upper=s.get('ci_upper'),
            ))
        
        # 汇总行 log 转换
        if effect_type in ['RR', 'OR', 'HR']:
            ln_pooled = math.log(max(pooled.get('effect', 1), 0.001))
            ln_pooled_low = math.log(max(pooled.get('ci_lower', 0.001), 0.001))
            ln_pooled_high = math.log(pooled.get('ci_upper', 1))
        else:
            ln_pooled = pooled.get('effect', 0)
            ln_pooled_low = pooled.get('ci_lower', 0)
            ln_pooled_high = pooled.get('ci_upper', 0)
        
        summary_line = 0.0 if effect_type in ['RR', 'OR', 'HR'] else 0.0
        
        return ForestPlotData(
            studies=plot_studies,
            pooled_effect=ln_pooled,
            pooled_ci_lower=ln_pooled_low,
            pooled_ci_upper=ln_pooled_high,
            pooled_pvalue=pooled.get('pvalue', 0),
            heterogeneity=heterogeneity,
            model=model,
            effect_type=effect_type,
            summary_line=summary_line,
        )
    
    def to_revman(self, data: ForestPlotData) -> str:
        """
        导出为 Cochrane RevMan 5 兼容格式
        RevMan 使用 XML-like 格式导入数据
        """
        lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<RevMan5Data>",
            "  <Analyses>",
            "    <Analysis id=\"1\" name=\"Meta-analysis\">",
            f"      <EffectMeasure type=\"{data.effect_type}\"/>",
            f"      <Model type=\"{'Random' if data.model == 'random' else 'Fixed'}\"/>",
            "      <Data>",
        ]
        
        for s in data.studies:
            year = str(s.year) if s.year else ""
            n = str(s.n_total) if s.n_total else ""
            e = str(s.n_events) if s.n_events else ""
            
            # 原始效应量（不是 log）
            eff = s.effect_raw if s.effect_raw is not None else math.exp(s.effect)
            ci_l = s.ci_raw_lower if s.ci_raw_lower is not None else math.exp(s.ci_lower)
            ci_u = s.ci_raw_upper if s.ci_raw_upper is not None else math.exp(s.ci_upper)
            
            lines.append(
                f"        <Study name=\"{s.name}\" year=\"{year}\">"
                f"<N total=\"{n}\" events=\"{e}\"/>"
                f"<Effect value=\"{eff:.3f}\" ci_lower=\"{ci_l:.3f}\" ci_upper=\"{ci_u:.3f}\"/>"
                f"<Weight>{s.weight:.2f}</Weight>"
                f"</Study>"
            )
        
        # 汇总
        pooled_eff = math.exp(data.pooled_effect) if data.effect_type in ['RR','OR','HR'] else data.pooled_effect
        pooled_low = math.exp(data.pooled_ci_lower) if data.effect_type in ['RR','OR','HR'] else data.pooled_ci_lower
        pooled_high = math.exp(data.pooled_ci_upper) if data.effect_type in ['RR','OR','HR'] else data.pooled_ci_upper
        
        lines.extend([
            "      </Data>",
            f"      <SummaryEffect value=\"{pooled_eff:.3f}\" "
            f"ci_lower=\"{pooled_low:.3f}\" ci_upper=\"{pooled_high:.3f}\" "
            f"pvalue=\"{data.pooled_pvalue:.4f}\"/>",
            "    </Analysis>",
            "  </Analyses>",
            "</RevMan5Data>",
        ])
        
        return '\n'.join(lines)
    
    def to_stata(self, data: ForestPlotData) -> str:
        """
        导出为 Stata meta 命令的 input 格式
        """
        lines = [
            "* Stata meta analysis input",
            "* Effect type: " + data.effect_type,
            "* Model: " + data.model,
            "",
            "input str50 study year effect selogci lower upper weight",
        ]
        
        for s in data.studies:
            name = f'"{s.name}"'
            year = s.year or 0
            eff = s.effect_raw if s.effect_raw is not None else math.exp(s.effect)
            se = (s.ci_upper - s.ci_lower) / (2 * 1.96)
            selog = se
            lower = s.ci_raw_lower if s.ci_raw_lower is not None else math.exp(s.ci_lower)
            upper = s.ci_raw_upper if s.ci_raw_upper is not None else math.exp(s.ci_upper)
            
            lines.append(f"{name} {year} {eff:.4f} {selog:.4f} {lower:.4f} {upper:.4f} {s.weight:.2f}")
        
        # 汇总行
        peff = math.exp(data.pooled_effect)
        plower = math.exp(data.pooled_ci_lower)
        pupper = math.exp(data.pooled_ci_upper)
        lines.append(f'"Summary" . {peff:.4f} . {plower:.4f} {pupper:.4f} .')
        
        lines.extend([
            "end",
            "",
            f"* Pooled effect: {peff:.4f} (95% CI: {plower:.4f}–{pupper:.4f})",
            f"* Heterogeneity: I²={data.heterogeneity.get('i2','N/A')}%, p={data.heterogeneity.get('p','N/A')}",
        ])
        
        return '\n'.join(lines)
