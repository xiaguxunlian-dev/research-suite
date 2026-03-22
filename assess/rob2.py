"""
RoB 2 — 随机对照试验偏倚风险评估工具
来源: Cochrane RoB 2 (Risk of Bias 2)
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class RoB2Result:
    """RoB 2 评估结果"""
    paper_title: str
    paper_id: str
    
    # 五项核心评估
    randomization: str = "Unknown"     # D1: 随机化过程
    allocation: str = "Unknown"        # D2: 干预分配
    blinding_participants: str = "Unknown"  # D3: 参与者盲法
    blinding_outcome: str = "Unknown"   # D4: 结果评估盲法
    attrition: str = "Unknown"         # D5: 结果数据完整性
    reporting: str = "Unknown"         # D6: 选择性报告
    other: str = "Unknown"             # D7: 其他偏倚
    
    # 综合判定
    overall: str = "Unknown"            # Low / Some concerns / High
    
    # 详细说明
    comments: str = ""
    assessor: str = "ResearchSuite AI"
    
    def to_markdown(self) -> str:
        level_emoji = {'Low': '✅', 'Some concerns': '⚠️', 'High': '❌', 'Unknown': '❓'}
        lines = [
            f"## RoB 2 质量评估: {self.paper_title[:60]}",
            "",
            f"| 评估维度 | 判定 |",
            f"|----------|------|",
            f"| D1 随机化过程 | {level_emoji.get(self.randomization,'❓')} {self.randomization} |",
            f"| D2 干预分配隐蔽 | {level_emoji.get(self.allocation,'❓')} {self.allocation} |",
            f"| D3 参与者盲法 | {level_emoji.get(self.blinding_participants,'❓')} {self.blinding_participants} |",
            f"| D4 结果评估盲法 | {level_emoji.get(self.blinding_outcome,'❓')} {self.blinding_outcome} |",
            f"| D5 结果数据完整性 | {level_emoji.get(self.attrition,'❓')} {self.attrition} |",
            f"| D6 选择性报告 | {level_emoji.get(self.reporting,'❓')} {self.reporting} |",
            f"| D7 其他偏倚 | {level_emoji.get(self.other,'❓')} {self.other} |",
            "",
            f"**综合判定: {level_emoji.get(self.overall,'❓')} {self.overall}**",
            "",
        ]
        if self.comments:
            lines.append(f"**备注**: {self.comments}")
            lines.append("")
        return '\n'.join(lines)


class RoB2Assessor:
    """
    RoB 2 评估器
    
    使用 LLM 辅助，根据 RCT 的方法描述自动判定偏倚风险。
    也支持人工逐项评估。
    """
    
    DOMAINS = [
        ('randomization', 'D1 随机化过程', [
            '是否正确生成随机分配序列？',
            '是否在分配前确保分组不可预测？',
        ]),
        ('allocation', 'D2 干预分配隐蔽', [
            '分配序列是否被隐藏直到干预分配？',
            '是否有足够的分配隐藏机制？',
        ]),
        ('blinding_participants', 'D3 参与者盲法', [
            '参与者是否知道自己的分组？',
            '是否采用了盲法设计？',
        ]),
        ('blinding_outcome', 'D4 结果评估盲法', [
            '结果评估者是否知道分组？',
            '结局指标是否可能被知晓分组影响？',
        ]),
        ('attrition', 'D5 结果数据完整性', [
            '是否有脱落/失访？',
            '是否使用了意向性分析（ITT）？',
            '脱落率是否超过20%且未做处理？',
        ]),
        ('reporting', 'D6 选择性报告', [
            '是否预先注册了研究方案？',
            '报告的结果是否与方案一致？',
        ]),
        ('other', 'D7 其他偏倚', [
            '是否有利益冲突？',
            '是否有其他系统性偏倚？',
        ]),
    ]
    
    def assess_file(self, file_path: str) -> RoB2Result:
        """从文件读取论文内容进行评估"""
        from pathlib import Path
        content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
        return self.assess_text(content)
    
    def assess_text(self, text: str, title: str = "Unknown") -> RoB2Result:
        """
        根据文本内容进行 RoB 2 评估
        
        Args:
            text: 论文全文或方法部分
            title: 论文标题
        
        Returns:
            RoB2Result 评估结果
        """
        text_lower = text.lower()
        
        # 启发式判断（可替换为 LLM 调用）
        result = RoB2Result(paper_title=title, paper_id="")
        
        # D1 随机化
        if any(k in text_lower for k in ['randomized', 'rct', 'random number', 'computer-generated', 'stratified', 'block randomization']):
            if any(k in text_lower for k in ['sealed envelope', 'central randomization', 'interactive web', 'automated system']):
                result.randomization = "Low"
            else:
                result.randomization = "Some concerns"
        elif any(k in text_lower for k in ['quasi-random', 'alternation', 'date of birth', 'case number']):
            result.randomization = "High"
        
        # D2 分配隐藏
        if any(k in text_lower for k in ['allocation concealment', 'opaque sealed envelope', 'central pharmacy', 'interactive voice']):
            result.allocation = "Low"
        elif any(k in text_lower for k in ['open-label', 'not concealed', 'envelope']):
            result.allocation = "High"
        
        # D3 参与者盲法
        if 'double-blind' in text_lower or ('single-blind' in text_lower and 'double' not in text_lower):
            if 'placebo' in text_lower:
                result.blinding_participants = "Low"
            else:
                result.blinding_participants = "Some concerns"
        elif 'open-label' in text_lower or 'unblinded' in text_lower or 'no blinding' in text_lower:
            result.blinding_participants = "High"
        
        # D4 评估者盲法
        if 'double-blind' in text_lower:
            result.blinding_outcome = "Low"
        elif 'outcome assessor' in text_lower or 'central adjudication' in text_lower:
            result.blinding_outcome = "Low"
        elif 'open-label' in text_lower:
            result.blinding_outcome = "High"
        
        # D5 数据完整性
        attrition_kw = ['dropout', 'lost to follow', 'withdrawal', 'attrition', 'excluded analysis']
        has_attrition = any(k in text_lower for k in attrition_kw)
        if not has_attrition:
            result.attrition = "Low"
        else:
            # 检查是否有 ITT
            if any(k in text_lower for k in ['intention-to-treat', 'itt analysis', 'full analysis set']):
                result.attrition = "Low"
            else:
                result.attrition = "Some concerns"
        
        # D6 选择性报告
        if any(k in text_lower for k in ['clinicaltrials.gov', 'prospero', 'registration', 'pre-specified', 'protocol']):
            result.reporting = "Low"
        else:
            result.reporting = "Some concerns"
        
        # D7 其他
        if any(k in text_lower for k in ['funded by', 'conflict of interest', 'disclosure']):
            if any(k in text_lower for k in ['no conflict', 'independently']):
                result.other = "Low"
            else:
                result.other = "Some concerns"
        
        # 综合判定
        concerns = sum(1 for d in [
            result.randomization, result.allocation, result.blinding_participants,
            result.blinding_outcome, result.attrition, result.reporting, result.other
        ] if d in ['Some concerns', 'High'])
        
        if concerns == 0:
            result.overall = "Low"
        elif concerns <= 2:
            result.overall = "Some concerns"
        else:
            result.overall = "High"
        
        return result
    
    def assess_interactive(self, title: str) -> RoB2Result:
        """交互式评估 — 逐项询问用户"""
        result = RoB2Result(paper_title=title, paper_id="")
        
        print("\n" + "="*50)
        print(f"RoB 2 评估: {title}")
        print("="*50)
        
        for field_name, label, questions in self.DOMAINS:
            print(f"\n{label}")
            for q in questions:
                print(f"  - {q}")
            print(f"  选项: Low / Some concerns / High / Unknown")
            val = input(f"  你的选择: ").strip()
            if val in ['Low', 'Some concerns', 'High', 'Unknown']:
                setattr(result, field_name, val)
        
        # 重新计算综合
        concerns = sum(1 for d in [
            result.randomization, result.allocation, result.blinding_participants,
            result.blinding_outcome, result.attrition, result.reporting, result.other
        ] if d in ['Some concerns', 'High'])
        result.overall = "Low" if concerns == 0 else ("Some concerns" if concerns <= 2 else "High")
        
        print("\n✅ 评估完成！")
        print(result.to_markdown())
        return result
