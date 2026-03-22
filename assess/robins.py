"""
ROBINS-I — 非随机化干预研究的偏倚风险评估
来源: Cochrane ROBINS-I Tool
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RoBINSIResult:
    """ROBINS-I 评估结果"""
    paper_title: str
    paper_id: str
    
    confounding: str = "Unknown"       # D1: 混杂因素
    selection: str = "Unknown"          # D2: 研究对象选择
    classification: str = "Unknown"    # D3: 干预分类
    deviation: str = "Unknown"          # D4: 干预偏离
    missing: str = "Unknown"            # D5: 数据缺失
    outcome: str = "Unknown"            # D6: 结果测量
    reporting: str = "Unknown"          # D7: 选择性报告
    
    overall: str = "Unknown"            # Low / Moderate / Serious / Critical
    nri_rating: str = ""                # No NI = Serious / Critical only
    
    def to_markdown(self) -> str:
        level_map = {
            'Low': '✅', 'Moderate': '⚠️', 'Serious': '❗', 'Critical': '🚨', 'Unknown': '❓'
        }
        lines = [
            f"## ROBINS-I 质量评估: {self.paper_title[:60]}",
            "",
            f"| 评估维度 | 判定 |",
            f"|----------|------|",
            f"| D1 混杂因素 | {level_map.get(self.confounding,'❓')} {self.confounding} |",
            f"| D2 选择偏倚 | {level_map.get(self.selection,'❓')} {self.selection} |",
            f"| D3 干预分类 | {level_map.get(self.classification,'❓')} {self.classification} |",
            f"| D4 干预偏离 | {level_map.get(self.deviation,'❓')} {self.deviation} |",
            f"| D5 数据缺失 | {level_map.get(self.missing,'❓')} {self.missing} |",
            f"| D6 结果测量 | {level_map.get(self.outcome,'❓')} {self.outcome} |",
            f"| D7 选择性报告 | {level_map.get(self.reporting,'❓')} {self.reporting} |",
            "",
            f"**综合判定: {level_map.get(self.overall,'❓')} {self.overall}**",
        ]
        return '\n'.join(lines)


class RoBINSIAssessor:
    """
    ROBINS-I 评估器 — 适用于非随机化干预研究（队列研究、病例对照等）
    """
    
    DOMAINS = [
        ('confounding', 'D1 混杂因素', [
            '是否控制了已知的混杂因素？',
            '是否使用了适当的统计方法控制混杂？',
            '重要混杂因素（年龄、性别、基础疾病）是否被控制？',
        ]),
        ('selection', 'D2 研究对象选择', [
            '纳入标准是否合理？',
            '是否存在健康工作者效应？',
            '是否发生了错误分类？',
        ]),
        ('classification', 'D3 干预分类', [
            '干预的定义是否清晰？',
            '是否区分了暴露与干预时机？',
            '是否存在暴露误分类？',
        ]),
        ('deviation', 'D4 干预偏离', [
            '受试者是否按原定方案接受干预？',
            '是否有交叉（crossover）或沾染？',
            '是否有违背方案的情况？',
        ]),
        ('missing', 'D5 数据缺失', [
            '是否有数据缺失？',
            '缺失数据是否影响了结果？',
            '是否使用了恰当的方法处理缺失数据？',
        ]),
        ('outcome', 'D6 结果测量', [
            '结局指标的定义是否有效？',
            '是否使用了客观的测量方法？',
            '结果评估者是否知晓干预分组？',
        ]),
        ('reporting', 'D7 选择性报告', [
            '是否预先定义了分析计划？',
            '报告的结果是否与计划一致？',
        ]),
    ]
    
    def assess_file(self, file_path: str) -> RoBINSIResult:
        from pathlib import Path
        content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
        return self.assess_text(content)
    
    def assess_text(self, text: str, title: str = "Unknown") -> RoBINSIResult:
        """基于文本自动评估 ROBINS-I"""
        text_lower = text.lower()
        result = RoBINSIResult(paper_title=title, paper_id="")
        
        # D1 混杂因素
        confounding_keywords = {
            'Low': ['propensity score', 'multivariate', 'adjusted for', 'covariates', 'stratified analysis', 'matched'],
            'Serious': ['unadjusted', 'crude', 'no adjustment', 'not controlled'],
        }
        if any(k in text_lower for k in confounding_keywords['Low']):
            result.confounding = "Low"
        elif any(k in text_lower for k in confounding_keywords['Serious']):
            result.confounding = "Serious"
        elif any(k in text_lower for k in ['adjustment', 'control for', 'regression']):
            result.confounding = "Moderate"
        
        # D2 选择偏倚
        if 'prospective' in text_lower or 'cohort' in text_lower:
            if 'consecutive' in text_lower or 'population-based' in text_lower:
                result.selection = "Low"
            else:
                result.selection = "Moderate"
        elif 'case-control' in text_lower:
            result.selection = "Moderate"
        
        # D3 干预分类
        if 'prospective' in text_lower or 'longitudinal' in text_lower:
            result.classification = "Low"
        elif 'retrospective' in text_lower:
            result.classification = "Serious"
        
        # D4 干预偏离
        if 'per protocol' in text_lower or 'as-treated' in text_lower:
            result.deviation = "Serious"
        elif 'intention-to-treat' in text_lower:
            result.deviation = "Low"
        
        # D5 数据缺失
        if 'complete case' in text_lower and 'multiple imputation' in text_lower:
            result.missing = "Low"
        elif 'missing data' in text_lower or 'lost to follow' in text_lower:
            result.missing = "Moderate"
        
        # D6 结果测量
        if 'blinded' in text_lower or 'independent' in text_lower:
            result.outcome = "Low"
        elif 'self-reported' in text_lower:
            result.outcome = "Moderate"
        
        # D7 选择性报告
        if any(k in text_lower for k in ['clinicaltrials.gov', 'registration', 'protocol', 'prospero']):
            result.reporting = "Low"
        else:
            result.reporting = "Moderate"
        
        # 综合判定
        serious_count = sum(1 for d in [
            result.confounding, result.selection, result.classification,
            result.deviation, result.missing, result.outcome, result.reporting
        ] if d in ['Serious', 'Critical'])
        
        if serious_count == 0:
            result.overall = "Low"
        elif serious_count == 1:
            result.overall = "Moderate"
        elif serious_count <= 3:
            result.overall = "Serious"
        else:
            result.overall = "Critical"
        
        return result
    
    def assess_interactive(self, title: str) -> RoBINSIResult:
        """交互式评估"""
        result = RoBINSIResult(paper_title=title, paper_id="")
        options = ['Low', 'Moderate', 'Serious', 'Critical', 'Unknown']
        
        print(f"\n{'='*50}\nROBINS-I 评估: {title}\n{'='*50}")
        for field_name, label, _ in self.DOMAINS:
            print(f"\n{label}")
            for opt in options:
                print(f"  [{options.index(opt)+1}] {opt}")
            try:
                choice = int(input("选择: ")) - 1
                if 0 <= choice < len(options):
                    setattr(result, field_name, options[choice])
            except ValueError:
                pass
        
        print("\n✅ 评估完成！")
        print(result.to_markdown())
        return result
