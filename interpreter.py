#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卦象解读增强模块
提供智能解读、吉凶判断、事项分析等功能
"""

from logger import info, debug


class GuaInterpreter:
    """卦象解读器"""
    
    # 传统吉凶卦分类
    AUSPICIOUS_GUA = [
        '乾为天', '地天泰', '风天小畜', '天火同人', '水天需',
        '天泽履', '地天泰', '雷天大壮', '风地观', '火天大有',
        '地山谦', '雷地豫', '泽地萃', '风雷益', '天风姤'
    ]
    
    INAUSPICIOUS_GUA = [
        '天地否', '天水讼', '坎为水', '水地比', '山风蛊',
        '泽水困', '水雷屯', '山水蒙', '风山渐', '雷泽归妹',
        '火山旅', '风火家人', '地火明夷', '水山蹇'
    ]
    
    # 事项关键词分类
    TOPIC_CATEGORIES = {
        'wealth': ['财', '钱', '投资', '生意', '财运', '求财', '赚', '赔'],
        'love': ['感情', '婚', '恋', '爱', '桃花', '姻缘', '复合', '单身'],
        'career': ['事业', '工作', '职', '官', '升', '跳槽', '创业'],
        'health': ['健康', '病', '身体', '医', '疾', '寿'],
        'study': ['学业', '考试', '学', '文', '名', '考'],
        'travel': ['出行', '旅', '远', '走', '动', '迁'],
    }
    
    def __init__(self):
        self.interpretations = self._load_interpretations()
    
    def _load_interpretations(self):
        """加载解读数据"""
        # 这里可以扩展为从文件加载详细解读
        return {}
    
    def interpret(self, result, topic=''):
        """智能解读
        
        Args:
            result: 起卦结果字典
            topic: 占卜事项
            
        Returns:
            解读文本
        """
        ben_gua = result.get('ben_gua', {})
        bian_gua = result.get('bian_gua')
        dong_yao = result.get('dong_yao', [])
        
        # 判断事项类型
        topic_type = self._classify_topic(topic)
        
        # 构建解读
        text = ""
        
        # 1. 吉凶判断
        fortune = self.judge_fortune(result)
        text += f"[b]▌吉凶判断[/b]\n"
        text += f"{fortune['level']} {fortune['emoji']} ({fortune['score']}分)\n"
        text += f"建议：{fortune['advice']}\n\n"
        
        # 2. 卦象分析
        text += f"[b]▌卦象分析[/b]\n"
        text += f"本卦：{ben_gua.get('name')} - {self._get_gua_meaning(ben_gua.get('name'))}\n"
        
        if bian_gua:
            text += f"变卦：{bian_gua.get('name')} - {self._get_gua_meaning(bian_gua.get('name'))}\n"
        
        text += f"动爻：{len(dong_yao)}爻\n\n"
        
        # 3. 事项解读
        text += f"[b]▌{self._get_topic_name(topic_type)}解读[/b]\n"
        text += self._interpret_by_topic(result, topic_type, topic)
        
        text += "\n"
        
        # 4. 传统断语
        text += f"[b]▌传统断语[/b]\n"
        text += self._get_traditional_judgment(result)
        
        return text
    
    def _classify_topic(self, topic):
        """分类事项类型
        
        Returns:
            'wealth' | 'love' | 'career' | 'health' | 'study' | 'travel' | 'general'
        """
        if not topic:
            return 'general'
        
        for topic_type, keywords in self.TOPIC_CATEGORIES.items():
            for keyword in keywords:
                if keyword in topic:
                    debug(f'事项类型：{topic} -> {topic_type}')
                    return topic_type
        
        return 'general'
    
    def _get_topic_name(self, topic_type):
        """获取事项类型名称"""
        names = {
            'wealth': '财运',
            'love': '感情',
            'career': '事业',
            'health': '健康',
            'study': '学业',
            'travel': '出行',
            'general': '综合'
        }
        return names.get(topic_type, '综合')
    
    def judge_fortune(self, result):
        """判断卦象吉凶
        
        Returns:
            {
                'level': '大吉'|'吉'|'平'|'凶'|'大凶',
                'emoji': '✅'|'⚠️'|'❌',
                'score': 0-100,
                'advice': '建议文本'
            }
        """
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        bian_gua = result.get('bian_gua')
        dong_yao = result.get('dong_yao', [])
        
        score = 50  # 基础分
        level = '平'
        emoji = '⚪'
        
        # 本卦吉凶
        if ben_gua_name in self.AUSPICIOUS_GUA:
            score += 30
        elif ben_gua_name in self.INAUSPICIOUS_GUA:
            score -= 30
        
        # 动爻数量影响
        dong_count = len(dong_yao)
        if dong_count == 0:
            score += 10  # 六爻皆静，稳定
        elif dong_count >= 4:
            score -= 10  # 多动，变化大
        
        # 变卦影响
        if bian_gua:
            bian_name = bian_gua.get('name', '')
            if bian_name in self.AUSPICIOUS_GUA:
                score += 15  # 变好
            elif bian_name in self.INAUSPICIOUS_GUA:
                score -= 15  # 变坏
        
        # 限制分数范围
        score = max(0, min(100, score))
        
        # 确定等级
        if score >= 80:
            level = '大吉'
            emoji = '✅'
        elif score >= 60:
            level = '吉'
            emoji = '👍'
        elif score >= 40:
            level = '平'
            emoji = '⚪'
        elif score >= 20:
            level = '凶'
            emoji = '⚠️'
        else:
            level = '大凶'
            emoji = '❌'
        
        # 生成建议
        advice = self._generate_advice(score, ben_gua_name, dong_count)
        
        return {
            'level': level,
            'emoji': emoji,
            'score': score,
            'advice': advice
        }
    
    def _generate_advice(self, score, gua_name, dong_count):
        """生成建议"""
        if score >= 80:
            return "运势正旺，宜积极进取，把握机会"
        elif score >= 60:
            return "运势平稳，可正常行事，注意细节"
        elif score >= 40:
            return "运势平平，宜守不宜攻，谨慎行事"
        elif score >= 20:
            return "运势欠佳，宜退守，避免冒险"
        else:
            return "运势低迷，宜静待时机，不宜妄动"
    
    def _get_gua_meaning(self, gua_name):
        """获取卦象基本含义"""
        meanings = {
            '乾为天': '刚健中正，自强不息',
            '坤为地': '柔顺承载，厚德载物',
            '水雷屯': '初始艰难，积蓄力量',
            '山水蒙': '蒙昧待启，需要学习',
            '水天需': '等待时机，不宜冒进',
            '天水讼': '争执不和，宜和解',
            '地水师': '统领众人，需要威严',
            '水地比': '亲密互助，合作共赢',
            '风天小畜': '小有积蓄，等待发展',
            '天泽履': '谨慎行事，如履薄冰',
            '地天泰': '通达顺利，阴阳和合',
            '天地否': '闭塞不通，宜退守',
            '天火同人': '志同道合，合作共赢',
            '火天大有': '大有所获，运势正旺',
            '地山谦': '谦虚谨慎，受益良多',
            '雷地豫': '愉悦安乐，顺势而为',
            '泽雷随': '随遇而安，顺势而为',
            '山风蛊': '积弊已久，需要改革',
            '地泽临': '居高临下，把握主动',
            '风地观': '观察等待，不宜妄动',
            '火雷噬嗑': '排除障碍，需要决断',
            '山火贲': '文饰外表，注重实质',
            '山地剥': '剥落衰败，宜守不宜攻',
            '地雷复': '复兴回归，重新开始',
            '天雷无妄': '无妄之灾，宜守正',
            '山天大畜': '大有积蓄，时机成熟',
            '山雷颐': '修身养性，注重内在',
            '泽风大过': '过度非常，需要调整',
            '坎为水': '险阻重重，需要勇气',
            '离为火': '光明依附，需要依托',
            '泽山咸': '感应相通，情感交流',
            '雷风恒': '恒久不变，持之以恒',
            '天山遁': '退避隐忍，等待时机',
            '雷天大壮': '强盛壮大，宜进取',
            '火地晋': '晋升发展，蒸蒸日上',
            '地火明夷': '光明受损，宜隐忍',
            '风火家人': '家庭和睦，内部团结',
            '火泽睽': '背离不合，需要沟通',
            '水山蹇': '艰难险阻，需要耐心',
            '雷水解': '解脱困难，雨过天晴',
            '山泽损': '损失减少，舍小得大',
            '风雷益': '受益良多，互利共赢',
            '泽天夬': '决断时刻，需要果断',
            '天风姤': '不期而遇，需要注意',
            '泽地萃': '聚集汇合，人才济济',
            '地风升': '上升发展，步步高升',
            '泽水困': '困顿艰难，需要坚持',
            '水风井': '井养不穷，稳定发展',
            '泽火革': '革故鼎新，需要变革',
            '火风鼎': '鼎立稳固，三足鼎立',
            '震为雷': '震动奋起，需要行动',
            '艮为山': '止而不动，需要静止',
            '风山渐': '循序渐进，不可急躁',
            '雷泽归妹': '归宿不当，需要谨慎',
            '雷火丰': '丰盛富足，运势正旺',
            '火山旅': '旅行在外，需要谨慎',
            '巽为风': '顺从进入，需要灵活',
            '兑为泽': '喜悦沟通，需要真诚',
            '风水涣': '涣散分离，需要凝聚',
            '水泽节': '节制约束，需要适度',
            '风泽中孚': '诚信中正，以诚待人',
            '雷山小过': '小有过失，需要谨慎',
            '水火既济': '事情完成，需要守成',
            '火水未济': '事情未成，需要努力'
        }
        return meanings.get(gua_name, '需要综合分析')
    
    def _interpret_by_topic(self, result, topic_type, topic=''):
        """根据事项类型解读"""
        ben_gua = result.get('ben_gua', {})
        bian_gua = result.get('bian_gua')
        dong_yao = result.get('dong_yao', [])
        
        interpretations = {
            'wealth': self._interpret_wealth,
            'love': self._interpret_love,
            'career': self._interpret_career,
            'health': self._interpret_health,
            'study': self._interpret_study,
            'travel': self._interpret_travel,
            'general': self._interpret_general
        }
        
        interpret_func = interpretations.get(topic_type, self._interpret_general)
        return interpret_func(result)
    
    def _interpret_wealth(self, result):
        """财运解读"""
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        
        # 财运好的卦
        wealth_gua = ['天火同人', '火天大有', '风天小畜', '地天泰', '天泽履']
        
        if ben_gua_name in wealth_gua:
            return "财运较好，适合投资理财，但需理性分析，不宜盲目跟风。正财稳定，偏财需谨慎。"
        elif ben_gua_name in self.INAUSPICIOUS_GUA:
            return "财运欠佳，不宜进行大额投资，保守理财为主。谨防诈骗和损失。"
        else:
            return "财运平稳，正常收支，不宜冒险投资。小额理财可以尝试。"
    
    def _interpret_love(self, result):
        """感情解读"""
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        
        # 感情好的卦
        love_gua = ['泽山咸', '雷风恒', '风火家人', '地天泰', '天火同人']
        
        if ben_gua_name in love_gua:
            return "感情运势良好，单身者有机会遇到合适对象。有伴侣者关系和睦，适合进一步发展。"
        elif ben_gua_name in ['天水讼', '火泽睽', '天地否']:
            return "感情易有争执，需要多沟通理解。单身者不宜急于确定关系。"
        else:
            return "感情运势平稳，顺其自然，不宜强求。真诚待人最重要。"
    
    def _interpret_career(self, result):
        """事业解读"""
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        
        # 事业好的卦
        career_gua = ['乾为天', '火天大有', '地天泰', '雷天大壮', '火地晋']
        
        if ben_gua_name in career_gua:
            return "事业运势旺盛，适合积极进取，有升职加薪或事业发展机会。把握良机。"
        elif ben_gua_name in ['天山遁', '地火明夷', '水山蹇']:
            return "事业遇到阻碍，宜退守等待，不宜贸然行动。积蓄力量，等待时机。"
        else:
            return "事业运势平稳，按部就班工作，不宜急于求成。稳扎稳打最重要。"
    
    def _interpret_health(self, result):
        """健康解读"""
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        
        if ben_gua_name in ['坎为水', '天地否', '山风蛊']:
            return "健康状况需关注，注意身体信号，有不适及时就医。避免过度劳累。"
        elif ben_gua_name in ['乾为天', '天火同人', '风天小畜']:
            return "健康状况良好，保持良好生活习惯即可。适当运动有益身心。"
        else:
            return "健康状况平稳，注意劳逸结合，保持良好心态。"
    
    def _interpret_study(self, result):
        """学业解读"""
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        
        if ben_gua_name in ['乾为天', '火天大有', '风地观', '山水蒙']:
            return "学业运势较好，学习效果佳，适合深入学习。考试发挥稳定。"
        elif ben_gua_name in ['坎为水', '天水讼']:
            return "学业遇到瓶颈，需要调整学习方法。不宜急于求成，循序渐进。"
        else:
            return "学业运势平稳，保持正常学习节奏即可。努力会有回报。"
    
    def _interpret_travel(self, result):
        """出行解读"""
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        
        if ben_gua_name in ['火山旅', '水山蹇', '坎为水']:
            return "出行需谨慎，注意安全，避免危险活动。延期或取消更稳妥。"
        elif ben_gua_name in ['地天泰', '天火同人', '风天小畜']:
            return "出行顺利，旅途愉快，可能遇到贵人。注意安全即可。"
        else:
            return "出行平稳，按正常计划进行即可。注意随身物品安全。"
    
    def _interpret_general(self, result):
        """综合解读"""
        ben_gua_name = result.get('ben_gua', {}).get('name', '')
        dong_count = len(result.get('dong_yao', []))
        
        if dong_count == 0:
            return "六爻皆静，局势稳定，宜守不宜攻。保持现状，等待时机。"
        elif dong_count >= 4:
            return "多爻发动，变化较多，需要灵活应对。不宜固执己见。"
        else:
            return "运势平稳，正常行事即可。把握机会，注意风险。"
    
    def _get_traditional_judgment(self, result):
        """获取传统断语"""
        # 这里可以扩展为从文件加载详细断语
        return "以上解读仅供参考，具体事宜需结合实际情况综合判断。"


# 全局单例
_interpreter = None

def get_interpreter():
    """获取解读器单例"""
    global _interpreter
    if _interpreter is None:
        _interpreter = GuaInterpreter()
    return _interpreter
