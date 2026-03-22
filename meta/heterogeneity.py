"""
异质性 (Heterogeneity) 统计计算器
计算 I²、Q 统计量、τ² (Tau-squared) 等 Meta 分析异质性指标
"""
import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class HeterogeneityResult:
    """异质性统计结果"""
    n_studies: int               # 研究数量
    q_statistic: float           # Cochran's Q 统计量
    df: int                      # 自由度 (n - 1)
    p_value: float               # Q 检验 p 值
    
    i_squared: float             # I² 异质性百分比 (0-100)
    h_squared: float             # H² 异质性比
    
    tau_squared: float           # τ² between-study variance
    tau: float                   # τ (tau)
    
    i2_label: str               # 描述性标签
    recommendation: str          # 效应量模型选择建议
    
    # 各研究权重
    weights: list[float]        # 逆方差权重列表
    
    def to_markdown(self) -> str:
        i2_emoji = "🟢" if self.i_squared < 25 else ("🟡" if self.i_squared < 75 else "🔴")
        
        lines = [
            "## 异质性分析结果",
            "",
            f"| 指标 | 数值 | 解释 |",
            f"|------|------|------|",
            f"| 研究数 (n) | {self.n_studies} | — |",
            f"| Cochran's Q | {self.q_statistic:.2f} | — |",
            f"| 自由度 (df) | {self.df} | — |",
            f"| p 值 | {self.p_value:.4f} | {'< 0.05 显著' if self.p_value < 0.05 else '≥ 0.05 不显著'} |",
            f"| **I²** | {i2_emoji} {self.i_squared:.1f}% | {self.i2_label} |",
            f"| H² | {self.h_squared:.2f} | — |",
            f"| τ² (tau²) | {self.tau_squared:.4f} | 组间方差 |",
            f"| τ (tau) | {self.tau:.4f} | 组间标准差 |",
            "",
            f"**模型选择建议**: {self.recommendation}",
            "",
        ]
        return '\n'.join(lines)


class HeterogeneityCalculator:
    """
    异质性统计计算器
    
    计算 Meta 分析中的关键异质性指标：
    - Cochran's Q 统计量
    - I² (Higgins' heterogeneity statistic)
    - τ² (between-study variance)
    - H² (heterogeneity ratio)
    """
    
    @staticmethod
    def calculate(
        effects: list[dict],
        method: str = 'dl',
    ) -> HeterogeneityResult:
        """
        计算异质性统计量
        
        Args:
            effects: 效应量列表，每个元素包含:
                - ln_rr: log(效应量) 或直接效应量
                - se: 标准误
                - vi: 方差 (= se²)
                - weight: 可选，手动权重
            method: 方差估计方法
                - 'dl': DerSimonian-Laird (默认)
                - 'fe': Fixed Effect
                - 'reml': Restricted Maximum Likelihood
        
        Returns:
            HeterogeneityResult 对象
        """
        n = len(effects)
        if n < 2:
            raise ValueError("需要至少2项研究才能计算异质性")
        
        # 提取 ln(RR) 和方差
        ln_rrs = []
        variances = []
        weights = []
        
        for e in effects:
            ln_rr = e.get('ln_rr') or e.get('effect') or e.get('ln_or') or 0
            vi = e.get('vi') or e.get('variance')
            se = e.get('se')
            
            if vi is None and se is not None:
                vi = se ** 2
            elif vi is None and se is None:
                # 尝试从 ci 计算
                if 'ci_lower' in e and 'ci_upper' in e:
                    ci_low = e['ci_lower']
                    ci_high = e['ci_upper']
                    if ci_low and ci_high and ci_low > 0:
                        se = (math.log(ci_high) - math.log(ci_low)) / (2 * 1.96)
                        vi = se ** 2
            
            if vi and vi > 0:
                ln_rrs.append(ln_rr)
                variances.append(vi)
                weights.append(1 / vi)
        
        if len(ln_rrs) < 2:
            raise ValueError("无法从输入数据中提取足够的效应量和方差")
        
        ln_rrs = ln_rrs[:len(variances)]
        weights = weights[:len(ln_rrs)]
        
        # 1. 计算加权平均效应量
        sum_w = sum(weights)
        sum_wy = sum(w * y for w, y in zip(weights, ln_rrs))
        pooled_effect = sum_wy / sum_w
        
        # 2. Cochran's Q 统计量
        q_stat = sum(w * (y - pooled_effect) ** 2 for w, y in zip(weights, ln_rrs))
        df = len(weights) - 1
        
        # 3. 计算 p 值 (Q 服从卡方分布)
        p_value = _chi2_cdf(q_stat, df)
        
        # 4. 计算 I²
        # I² = max(0, (Q - df) / Q * 100)
        if q_stat > 0:
            i_squared = max(0, (q_stat - df) / q_stat * 100)
        else:
            i_squared = 0
        
        # 5. H² = Q / df
        h_squared = q_stat / df if df > 0 else 1
        
        # 6. τ² (DerSimonian-Laird estimator)
        if q_stat > df:
            tau_sq = max(0, (q_stat - df) / (sum_w - sum(w**2) / sum_w))
        else:
            tau_sq = 0
        
        tau = math.sqrt(tau_sq)
        
        # 7. I² 描述性标签
        if i_squared < 25:
            i2_label = "低异质性"
        elif i_squared < 50:
            i2_label = "中度异质质性"
        elif i_squared < 75:
            i2_label = "较高异质性"
        else:
            i2_label = "高度异质性"
        
        # 8. 模型选择建议
        if p_value < 0.1 or i_squared > 50:
            recommendation = "🔴 推荐使用随机效应模型 (Random Effects)"
        else:
            recommendation = "🟢 可使用固定效应模型 (Fixed Effect)，但随机效应更稳健"
        
        # 9. 标准化权重（百分比）
        total_w = sum(weights)
        norm_weights = [w / total_w * 100 for w in weights]
        
        return HeterogeneityResult(
            n_studies=n,
            q_statistic=q_stat,
            df=df,
            p_value=p_value,
            i_squared=i_squared,
            h_squared=h_squared,
            tau_squared=tau_sq,
            tau=tau,
            i2_label=i2_label,
            recommendation=recommendation,
            weights=norm_weights,
        )


# ---- 以下为内部辅助函数 ----

def _chi2_cdf(x: float, df: int) -> float:
    """
    计算卡方分布的 CDF (累计分布函数)
    使用 Wilson-Hilferty 近似
    """
    if df <= 0 or x < 0:
        return 1.0 if x >= 0 else 0.0
    
    # 对于大 df 使用正态近似
    if df > 100:
        z = (pow(x / df, 1/3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
        return _normal_cdf(z)
    
    # 使用不完全伽马函数近似
    return _chi2_sdf_approx(x, df)


def _normal_cdf(z: float) -> float:
    """标准正态分布 CDF"""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _chi2_sdf_approx(x: float, df: int) -> float:
    """
    卡方分布生存函数的近似 (1 - CDF)
    使用不完全贝塔函数关系: Q(χ²|ν) ≈ 1 - I(ν/(ν+χ²), ν/2, 0.5)
    """
    if x <= 0:
        return 1.0
    
    a = df / 2.0
    z = df / (df + x)
    
    # 使用连分数近似不完全贝塔函数
    return _regularized_beta(z, a, 0.5)


def _regularized_beta(z: float, a: float, b: float) -> float:
    """
    正则化不完全贝塔函数 I_z(a,b) 的近似
    使用连分数表示法
    """
    max_iter = 200
    eps = 1e-10
    
    # 使用连分数近似
    d = 1 - (a + b) * z / (a + 1)
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1 / d
    h = d
    
    for m in range(1, max_iter):
        # 偶数步
        m2 = 2 * m
        aa = m * (b - m) * z / ((a + m2 - 1) * (a + m2))
        d = 1 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1 / d
        c = 1 + aa / (1 if abs(d) < 1e-30 else d)
        h *= d * c
        
        # 奇数步
        aa = -(a + m) * (a + b + m) * z / ((a + m2) * (a + m2 + 1))
        d = 1 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1 / d
        c = 1 + aa / d
        h *= d * c
        
        if abs(d * c - 1) < eps:
            break
    
    # 乘以 z^a * (1-z)^b / (a * B(a,b))
    result = math.exp(
        (a * math.log(z) if z > 0 else 0) +
        (b * math.log(1 - z) if z < 1 else 0) -
        math.lgamma(a) - math.lgamma(b) + math.lgamma(a + b)
    ) * h / a
    
    return max(0, min(1, result))
