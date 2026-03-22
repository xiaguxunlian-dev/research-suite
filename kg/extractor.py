"""
知识图谱实体关系抽取器
从论文文本中抽取「基因-疾病-药物-通路-症状」关系
支持 Neo4j / JSON / NetworkX 格式导出
"""
import re
import json
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Entity:
    """实体"""
    id: str
    name: str
    type: str           # gene / disease / drug / pathway / symptom / protein / cell
    aliases: list[str] = field(default_factory=list)
    source: str = ""    # 来源论文
    properties: dict = field(default_factory=dict)


@dataclass
class Relation:
    """关系"""
    source_id: str
    target_id: str
    type: str           # upregulates / downregulates / treats / causes / interacts / associates
    evidence: str = ""  # 证据文本
    paper: str = ""
    pmid: str = ""
    weight: float = 1.0  # 关系强度


@dataclass
class KnowledgeGraph:
    """知识图谱"""
    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def add_entity(self, entity: Entity):
        if not self.get_entity(entity.id):
            self.entities.append(entity)
    
    def add_relation(self, relation: Relation):
        self.relations.append(relation)
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        for e in self.entities:
            if e.id == entity_id:
                return e
        return None
    
    def entity_count(self) -> dict:
        counts = {}
        for e in self.entities:
            counts[e.type] = counts.get(e.type, 0) + 1
        return counts
    
    def to_neo4j_cypher(self) -> str:
        """生成 Neo4j Cypher 导入语句"""
        statements = []
        
        # 创建约束和索引
        statements.append("// 约束和索引")
        statements.append("CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;")
        statements.append("")
        
        # 创建实体节点
        statements.append("// 实体节点")
        for e in self.entities:
            type_label = e.type.capitalize()
            name_escaped = e.name.replace('"', "'").replace('\\', '\\\\')
            props = json.dumps(e.properties, ensure_ascii=False).replace('"', "'")
            alias_str = '|'.join(e.aliases) if e.aliases else ''
            
            stmt = (
                f"CREATE (e{'_'+type_label}:Entity:{type_label} {{"
                f"id: '{e.id}', name: '{name_escaped}', aliases: '{alias_str}', "
                f"source: '{e.source}'"
                f"}})"
            )
            statements.append(stmt)
        
        statements.append("")
        statements.append("// 关系")
        
        for r in self.relations:
            rel_type = r.type.upper().replace(' ', '_')
            src_escaped = r.source_id.replace("'", "\\'")
            tgt_escaped = r.target_id.replace("'", "\\'")
            ev_escaped = r.evidence[:200].replace("'", "\\'") if r.evidence else ""
            
            stmt = (
                f"MATCH (s {{id: '{src_escaped}'}}), (t {{id: '{tgt_escaped}'}}) "
                f"CREATE (s)-[r:{rel_type} {{"
                f"evidence: '{ev_escaped}', paper: '{r.paper}', "
                f"weight: {r.weight}, pmid: '{r.pmid}'"
                f"}}]->(t)"
            )
            statements.append(stmt)
        
        return '\n'.join(statements)
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
    
    def to_networkx(self) -> dict:
        """生成 NetworkX 兼容格式"""
        import networkx as nx
        
        G = nx.DiGraph()
        
        # 添加节点
        for e in self.entities:
            G.add_node(e.id, label=e.name, type=e.type, **e.properties)
        
        # 添加边
        for r in self.relations:
            G.add_edge(r.source_id, r.target_id,
                       relation=r.type, weight=r.weight,
                       evidence=r.evidence, paper=r.paper)
        
        return {
            'nodes': [{'id': n, **d} for n, d in G.nodes(data=True)],
            'edges': [{'source': u, 'target': v, **d} for u, v, d in G.edges(data=True)],
            'metadata': self.metadata,
        }


class EntityExtractor:
    """
    实体抽取器
    
    支持实体类型:
    - 基因 (gene)
    - 疾病 (disease)
    - 药物 (drug)
    - 蛋白 (protein)
    - 通路 (pathway)
    - 症状 (symptom)
    - 细胞类型 (cell)
    """
    
    # 字典匹配模式
    DICTIONARIES = {
        'gene': [
            'TP53', 'BRCA1', 'BRCA2', 'EGFR', 'KRAS', 'MYC', 'PTEN', 'APC',
            'HER2', 'PD-1', 'PD-L1', 'CTLA-4', 'VEGF', 'IL-6', 'TNF-α',
            'IFN-γ', 'IL-10', 'IL-1β', 'STAT3', 'AKT', 'mTOR', 'PI3K',
            'MAPK', 'ERK', 'JAK', 'STAT', 'BRAF', 'ALK', 'ROS1', 'NTRK',
            'BCL-2', 'BAX', 'CASPASE', 'PARP', 'CDK4', 'CDK6', 'CD8',
            'CD4', 'Treg', 'NK', 'DC', 'Macrophage', 'T cell',
        ],
        'disease': [
            'cancer', 'tumor', 'carcinoma', 'melanoma', 'lymphoma', 'leukemia',
            'diabetes', 'obesity', 'hypertension', 'cardiovascular', 'stroke',
            'Alzheimer', 'Parkinson', 'depression', 'anxiety', 'schizophrenia',
            'arthritis', 'asthma', 'COPD', 'fibrosis', 'cirrhosis',
            'infection', 'sepsis', 'COVID', 'influenza', 'tuberculosis',
        ],
        'drug': [
            'aspirin', 'ibuprofen', 'acetaminophen', 'metformin', 'insulin',
            'atorvastatin', 'rosuvastatin', 'lisinopril', 'amlodipine', 'metoprolol',
            'omeprazole', 'pantoprazole', 'metronidazole', 'azithromycin', 'ceftriaxone',
            'paclitaxel', 'doxorubicin', 'cisplatin', 'imatinib', 'rituximab',
            'trastuzumab', 'pembrolizumab', 'nivolumab', 'ipilimumab', 'nivolumab',
            'dexamethasone', 'prednisone', 'cyclosporine', 'tacrolimus', 'rapamycin',
        ],
        'pathway': [
            'PI3K/AKT', 'mTOR', 'MAPK', 'ERK', 'JAK/STAT', 'TGF-β', 'WNT',
            'NF-κB', 'HIF', 'AMPK', 'Notch', 'Hedgehog', 'Apoptosis',
            'Cell cycle', 'DNA repair', 'Angiogenesis', 'EMT', 'Immune checkpoint',
            'PD-1/PD-L1', 'CTLA-4', 'T cell receptor', 'B cell receptor',
            'Complement', 'Coagulation', 'Inflammatory', 'Oxidative stress',
        ],
        'symptom': [
            'fatigue', 'pain', 'fever', 'inflammation', 'edema', 'rash',
            'headache', 'nausea', 'vomiting', 'diarrhea', 'constipation',
            'dyspnea', 'cough', 'anemia', 'thrombocytopenia', 'neutropenia',
            'weight loss', 'weight gain', 'insomnia', 'anxiety', 'cognitive impairment',
        ],
    }
    
    # 正则抽取模式
    REGEX_PATTERNS = {
        'gene': [
            r'\b([A-Z]{2,}[0-9]?)\b',           # 全大写基因名如 TP53, EGFR
            r'\bgene\s+([A-Z]{2,})\b',          # gene ABC
        ],
        'protein': [
            r'\b([A-Z][a-z]{2,}[0-9]?)-([0-9])\b',  # Protein-1
        ],
        'drug': [
            r'\b([a-z]+)mab\b',                # 单抗药物 -mab 后缀
            r'\b([a-z]+)nib\b',                # 激酶抑制剂 -nib 后缀
            r'\b([a-z]+)statin\b',             # 他汀类
            r'\b([a-z]+)pril\b',              # ACEI
            r'\b([a-z]+)sartan\b',            # ARB
        ],
        'pathway': [
            r'\b(PI3K|AKT|mTOR|MAPK|ERK|JAK|STAT|NF-κB|WNT)\b(?:\s*pathway)?',
        ],
    }
    
    def extract_entities(self, text: str, pmid: str = "") -> list[Entity]:
        """从文本中抽取实体"""
        text_lower = text.lower()
        entities = []
        seen_ids = set()

        # 字典匹配（优先，覆盖面最广）
        for etype, terms in self.DICTIONARIES.items():
            for term in terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    eid = self._make_id(term, etype)
                    if eid not in seen_ids:
                        seen_ids.add(eid)
                        entities.append(Entity(
                            id=eid,
                            name=term,
                            type=etype,
                            source=pmid,
                            properties={'matched_by': 'dictionary'},
                        ))

        # 正则抽取（仅作为字典补充，要求名称 >= 3 字符且至少含数字或特定模式）
        for etype, patterns in self.REGEX_PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for m in matches:
                    name = m if isinstance(m, str) else m[0]
                    name = name.strip()
                    # 严格过滤：至少3字符，且包含数字或全大写（基因/蛋白特征）
                    if len(name) >= 3 and (any(c.isdigit() for c in name) or name.isupper()):
                        eid = self._make_id(name, etype)
                        if eid not in seen_ids:
                            seen_ids.add(eid)
                            entities.append(Entity(
                                id=eid,
                                name=name,
                                type=etype,
                                source=pmid,
                                properties={'matched_by': 'regex'},
                            ))

        return entities
    
    def _make_id(self, name: str, etype: str) -> str:
        return f"{etype}:{name.upper().replace(' ', '_').replace('-', '_')}"


class RelationExtractor:
    """
    关系抽取器
    
    从论文文本中抽取实体间关系
    支持的关系类型:
    - upregulates / activates (上调/激活)
    - downregulates / inhibits (下调/抑制)
    - treats / ameliorates (治疗)
    - causes / induces (导致/诱发)
    - interacts with (相互作用)
    - associates with (关联)
    - inhibits (抑制)
    - expresses (表达)
    - phosphorylates (磷酸化)
    """
    
    RELATION_PATTERNS = {
        'upregulates': [
            r'(\w+)\s+(?:significantly\s+)?(?:up[- ]?regulated|increased|elevated|enhanced|induced)\s+(?:in|by|through)?\s*(\w+)',
            r'(\w+)\s+(?:activates|stimulates)\s+(\w+)',
            r'(\w+)\s+(?:induces?|promotes?)\s+(?:the\s+)?(?:expression|activity|production)\s+of\s+(\w+)',
        ],
        'downregulates': [
            r'(\w+)\s+(?:down[- ]?regulated|decreased|reduced|suppressed|inhibited)\s+(?:in|by)?\s*(\w+)',
            r'(\w+)\s+(?:inhibits?|blocks?|antagonizes?)\s+(\w+)',
            r'(\w+)\s+(?:attenuates?|represses?)\s+(?:the\s+)?(?:expression|activity)\s+of\s+(\w+)',
        ],
        'treats': [
            r'(\w+)\s+(?:treats?|ameliorates?|alleviates?|improves?)\s+(?:the\s+)?(\w+)\s+(?:in|of)\s+(\w+)',
            r'(\w+)\s+(?:effective|efficient)\s+(?:in|against)\s+(\w+)',
            r'(\w+)\s+(?:therapy|treatment)\s+(?:for|in)\s+(\w+)',
        ],
        'causes': [
            r'(\w+)\s+(?:causes?|induces?|leads to|results in)\s+(\w+)',
            r'(\w+)\s+(?:associated\s+with|linked\s+to|risk\s+of)\s+(\w+)',
        ],
        'interacts': [
            r'(\w+)\s+(?:interacts?\s+with|binds?\s+to|complex(?:es)?\s+with)\s+(\w+)',
            r'(\w+)\s+(?:dimerizes?|heterozygotes?)\s+with\s+(\w+)',
        ],
        'phosphorylates': [
            r'(\w+)\s+(?:phosphorylates?)\s+(\w+)',
        ],
    }
    
    def extract_relations(
        self,
        text: str,
        entities: list[Entity],
        pmid: str = "",
    ) -> list[Relation]:
        """从文本中抽取关系"""
        entity_map = {e.name.upper(): e.id for e in entities}
        
        relations = []
        seen = set()
        
        for rel_type, patterns in self.RELATION_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for m in matches:
                    groups = m.groups()
                    if len(groups) >= 2:
                        src = groups[0].upper().strip()
                        tgt = groups[1].upper().strip()
                        
                        # 检查是否在实体列表中
                        src_id = entity_map.get(src) or entity_map.get(src[:-1]) if len(src) > 3 else None
                        tgt_id = entity_map.get(tgt) or entity_map.get(tgt[:-1]) if len(tgt) > 3 else None
                        
                        if src_id and tgt_id and src_id != tgt_id:
                            key = f"{src_id}|{rel_type}|{tgt_id}"
                            if key not in seen:
                                seen.add(key)
                                relations.append(Relation(
                                    source_id=src_id,
                                    target_id=tgt_id,
                                    type=rel_type,
                                    evidence=m.group(0)[:200],
                                    paper=pmid,
                                    weight=0.8,
                                ))
        
        return relations
