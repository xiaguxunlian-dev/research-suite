"""
效应量 (Effect Size) 提取与标准化模块
支持 RR, OR, HR, MD, SMD 的提取与转换
"""
import re
import math
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class EffectSize:
    """效应量数据结构"""
    raw_text: str                          # 原始文本
    type: str = "Unknown"                  # 类型: RR / OR / HR / MD / SMD / OR_RCT
    
    # 点估计与置信区间
    point_estimate: Optional[float] = None
    ci_lower: Optional[float] = None
    ci_upper: Optional[float] = None
    ci_level: float = 0.95
    
    # 标准误
    se: Optional[float] = None
    variance: Optional[float] = None
    
    # 统计显著性
    p_value: Optional[float] = None
    significant: bool = False
    
    # 标准化转换后
    ln_rr: Optional[float] = None           # log 转换后的 RR
    ln_ci_lower: Optional[float] = None
    ln_ci_upper: Optional[float] = None
    
    # 元分析用
    weight: float = 1.0                    # 逆方差权重
    sample_size: Optional[int] = None
    events_total: Optional[int] = None      # 总事件数
    n_total: Optional[int] = None          # 总样本量
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_markdown(self) -> str:
        sig = "✅ 显著" if self.significant else "❌ 不显著"
        return (
            f"**{self.type}**: {self.point_estimate} "
            f"(95% CI: {self.ci_lower}–{self.ci_upper}) {sig}"
        )


class EffectSizeExtractor:
    """
    从论文文本中提取标准化效应量
    
    支持提取：
    - Relative Risk (RR) 相对风险度
    - Odds Ratio (OR) 比值比
    - Hazard Ratio (HR) 风险比
    - Mean Difference (MD) 均数差
    - Standardized Mean Difference (SMD) 标准化均数差
    """
    
    # 匹配模式
    PATTERNS = {
        'RR': [
            r'RR\s*=\s*([0-9.]+)',
            r'relative risk\s*(?:of|is|:)?\s*([0-9.]+)',
            r'risk ratio\s*(?:of|is|:)?\s*([0-9.]+)',
            r'\bRR\b[:\s]+([0-9.]+)',
        ],
        'OR': [
            r'OR\s*=\s*([0-9.]+)',
            r'odds ratio\s*(?:of|is|:)?\s*([0-9.]+)',
            r'\bOR\b[:\s]+([0-9.]+)',
        ],
        'HR': [
            r'HR\s*=\s*([0-9.]+)',
            r'hazard ratio\s*(?:of|is|:)?\s*([0-9.]+)',
            r'\bHR\b[:\s]+([0-9.]+)',
        ],
        'MD': [
            r'mean difference\s*(?:of|:)?\s*([-+]?[0-9.]+)',
            r'difference in means[:\s]+([-+]?[0-9.]+)',
            r'MD\s*=\s*([-+]?[0-9.]+)',
        ],
        'SMD': [
            r'standardized mean difference[:\s]+([-+]?[0-9.]+)',
            r'SMD[:\s]+([-+]?[0-9.]+)',
            r"Cohen's d[:\s]+([-+]?[0-9.]+)",
        ],
    }
    
    # 置信区间模式
    CI_PATTERNS = [
        r'95%\s*CI[:\s]+([0-9.]+)\s*[-–to]+\s*([0-9.]+)',
        r'\(([0-9.]+)\s*[-–to]+\s*([0-9.]+)\)\s*95%\s*CI',
        r'CI\s*=\s*([0-9.]+)\s*[-–to]+\s*([0-9.]+)',
        r'([0-9.]+)\s*[-–to]+\s*([0-9.]+)\s*\(?\s*95%\s*%?\s*CI',
    ]
    
    def extract_all(self, text: str) -> list[EffectSize]:
        """从文本中提取所有效应量"""
        results = []
        text_lower = text.lower()
        
        for eff_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for m in matches:
                    es = EffectSize(raw_text=m.group(0), type=eff_type)
                    try:
                        es.point_estimate = float(m.group(1))
                    except (ValueError, IndexError):
                        continue
                    
                    # 尝试提取置信区间
                    ci_match = self._extract_ci(text, m.end(), m.start())
                    if ci_match:
                        es.ci_lower, es.ci_upper = ci_match
                    
                    # 提取 p 值
                    es.p_value = self._extract_pvalue(text, m.start(), m.end())
                    es.significant = es.p_value < 0.05 if es.p_value else False
                    
                    # 标准化转换
                    if eff_type in ['RR', 'OR', 'HR']:
                        if es.point_estimate and es.point_estimate > 0:
                            es.ln_rr = math.log(es.point_estimate)
                            if es.ci_lower and es.ci_upper:
                                es.ln_ci_lower = math.log(es.ci_lower)
                                es.ln_ci_upper = math.log(es.ci_upper)
                            # 计算 SE
                            if es.ln_ci_lower and es.ln_ci_upper:
                                es.se = (es.ln_ci_upper - es.ln_ci_lower) / (2 * 1.96)
                                es.variance = es.se ** 2
                    
                    results.append(es)
                    break  # 每种类型只取第一个匹配
        
        return results
    
    def _extract_ci(self, text: str, search_start: int, search_end: int) -> Optional[tuple]:
        """在效应量附近提取置信区间"""
        # 搜索范围：前后100个字符
        start = max(0, search_start - 50)
        end = min(len(text), search_end + 100)
        snippet = text[start:end]
        
        for pattern in self.CI_PATTERNS:
            m = re.search(pattern, snippet, re.IGNORECASE)
            if m:
                try:
                    lower = float(m.group(1))
                    upper = float(m.group(2))
                    if 0 < lower < upper < 1000:
                        return (lower, upper)
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_pvalue(self, text: str, start: int, end: int) -> Optional[float]:
        """提取 p 值"""
        snippet = text[max(0, start-50):min(len(text), end+50)]
        
        p_patterns = [
            r'p\s*[=<>]\s*([0-9.]+)',
            r'p[\s-]value\s*[=<>]\s*([0-9.]+)',
        ]
        
        for pattern in p_patterns:
            m = re.search(pattern, snippet, re.IGNORECASE)
            if m:
                try:
                    return float(m.group(1))
                except ValueError:
                    continue
        return None


class EffectSizeConverter:
    """
    效应量转换工具
    
    在 Meta 分析中，需要将不同效应量统一为同一类型进行合并
    """
    
    @staticmethod
    def rr_to_lnrr(rr: float) -> float:
        """RR -> log(RR)"""
        return math.log(rr) if rr > 0 else 0
    
    @staticmethod
    def or_to_lnor(or_val: float) -> float:
        """OR -> log(OR)"""
        return math.log(or_val) if or_val > 0 else 0
    
    @staticmethod
    def or_to_rr(or_val: float, p0: float) -> float:
        """
        OR -> RR (需要对照组事件率)
        使用公式: RR = OR / ((1 - p0) + p0 * OR)
        """
        if or_val <= 0 or p0 <= 0 or p0 >= 1:
            return None
        return or_val / ((1 - p0) + p0 * or_val)
    
    @staticmethod
    def hr_to_lnhr(hr: float) -> float:
        """HR -> log(HR)"""
        return math.log(hr) if hr > 0 else 0
    
    @staticmethod
    def variance_from_ci(effect: float, ci_low: float, ci_high: float, ci_level: float = 0.95) -> float:
        """
        从置信区间计算方差
        
        Args:
            effect: 点估计
            ci_low: 置信下限
            ci_high: 置信上限
            ci_level: 置信水平（默认0.95对应1.96）
        """
        if ci_low <= 0 or ci_high <= 0:
            return None
        # 对于 log 转化的效应量
        z = 1.96 if ci_level == 0.95 else 1.645 if ci_level == 0.90 else 2.576
        se = (math.log(ci_high) - math.log(ci_low)) / (2 * z)
        return se ** 2
    
    @staticmethod
    def variance_lnrr(ci_low: float, ci_high: float) -> float:
        """从 log RR 的置信区间计算方差"""
        z = 1.96
        se = (math.log(ci_high) - math.log(ci_low)) / (2 * z)
        return se ** 2
