from datetime import datetime

import streamlit as st


def clamp_confidence(value):
    return max(5, min(95, value))


def render_direction_panel(result):
    st.markdown("### 📈📉 资产方向速览")
    col_up, col_down = st.columns(2)

    with col_up:
        st.success("⬆️ 上涨概率更高")
        for item in result["上涨(↑)"]:
            st.write(f"- {item}")

    with col_down:
        st.error("⬇️ 下跌风险更高")
        for item in result["下跌(↓)"]:
            st.write(f"- {item}")


def build_single_report(event_name, result, confidence_offset):
    lines = [
        f"# 宏观推演简报 - {event_name}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 核心逻辑",
        result["核心逻辑"],
        "",
        "## 资产方向速览",
        "### 上涨(↑)",
    ]

    for item in result["上涨(↑)"]:
        lines.append(f"- {item}")

    lines.extend(["", "### 下跌(↓)"])
    for item in result["下跌(↓)"]:
        lines.append(f"- {item}")

    lines.extend(["", "## 传导链与置信度"])
    for idx, chain in enumerate(result["传导链条"]):
        score = clamp_confidence(result["链路置信度"][idx] + confidence_offset)
        lines.append(f"{idx + 1}. {chain} | 置信度: {score}%")

    lines.extend([
        "",
        "## 反转测试",
        result["反转测试"],
    ])
    return "\n".join(lines)


def build_compare_report(event_a, result_a, event_b, result_b):
    a_up = set(result_a["上涨(↑)"])
    b_up = set(result_b["上涨(↑)"])
    a_down = set(result_a["下跌(↓)"])
    b_down = set(result_b["下跌(↓)"])

    both_up = sorted(a_up & b_up)
    both_down = sorted(a_down & b_down)
    only_a_up = sorted(a_up - b_up)
    only_b_up = sorted(b_up - a_up)

    lines = [
        f"# 场景对比简报 - {event_a} VS {event_b}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"## 场景A: {event_a}",
        result_a["核心逻辑"],
        "",
        f"## 场景B: {event_b}",
        result_b["核心逻辑"],
        "",
        "## 交集与差异",
        "### 双场景共同上涨",
    ]

    if both_up:
        for item in both_up:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")

    lines.append("")
    lines.append("### 双场景共同下跌")
    if both_down:
        for item in both_down:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")

    lines.append("")
    lines.append(f"### 仅场景A上涨 ({event_a})")
    if only_a_up:
        for item in only_a_up:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")

    lines.append("")
    lines.append(f"### 仅场景B上涨 ({event_b})")
    if only_b_up:
        for item in only_b_up:
            lines.append(f"- {item}")
    else:
        lines.append("- 无")

    return "\n".join(lines)


def render_compare_card(title, event_name, result):
    st.markdown(f"#### {title}: {event_name}")
    st.info(result["核心逻辑"])

    col_up, col_down = st.columns(2)
    with col_up:
        st.markdown("**⬆️ 上涨**")
        for item in result["上涨(↑)"]:
            st.write(f"- {item}")

    with col_down:
        st.markdown("**⬇️ 下跌**")
        for item in result["下跌(↓)"]:
            st.write(f"- {item}")


# 页面配置
st.set_page_config(page_title="宏观逻辑推演罗盘", layout="centered")
st.title("🧭 宏观资产传导推演系统")
st.markdown("---")

# 宏观硬逻辑字典 (升级为“传导链”结构)
macro_rules = {
    "美联储加息 (或预期升温)": {
        "上涨(↑)": [
            "美元指数",
            "美债2年期收益率 (政策预期最敏感)",
            "美债10年期收益率 (多数跟涨)",
            "高股息/防御板块",
            "货币基金"
        ],
        "下跌(↓)": [
            "非美货币 (人民币等)",
            "黄金",
            "大宗商品 (铜/油)",
            "美股科技股/成长股"
        ],
        "传导链条": [
            "**【利率定价】** 紧缩预期起 ➡️ **美债2年期收益率 ↑** (先头部队) ➡️ **美债10年期收益率 ↑** (跟涨，但受衰退预期压制)",
            "**【汇率博弈】** 中美息差扩大 ➡️ **美元指数 ↑** 🔴反转压制🔴 **非美货币 (如人民币) ↓**",
            "**【大类资产】** 无风险收益率抬升 ➡️ **美元高息存款/货币基金 ↑** 🔴反转压制🔴 **黄金 / 铜油等大宗商品 ↓** (持有无息资产机会成本增加)",
            "**【股市风格】** 远期贴现率上行 🔴反转压制🔴 **美股科技股/成长股 ↓** (杀估值) 🔄资金跷跷板🔄 避险流入 **高股息/防御板块 ↑**"
        ],
        "链路置信度": [85, 80, 78, 75],
        "核心逻辑": "全球资金成本上升，流动性收紧。无风险收益率（美债）如同地心引力，引力变大，所有风险资产的估值泡沫和无息资产的价格都会被拽下来。",
        "反转测试": "1. 市场是否已提前100%定价？若是，落地瞬间反而是'利空出尽'的买点（买预期，卖事实）。\n2. 若加息是因为经济极其强劲（企业盈利增速 > 估值杀跌速度），美股可能短暂回调后继续走主升浪。"
    },
    "美联储降息 (或预期升温)": {
        "上涨(↑)": [
            "黄金",
            "美债2年期价格 (弹性通常更高)",
            "美债10年期价格",
            "非美货币",
            "大宗商品 (铜/油)",
            "科技/成长风格股票"
        ],
        "下跌(↓)": [
            "美元指数",
            "美债2年期收益率",
            "美债10年期收益率",
            "传统银行股利差"
        ],
        "传导链条": [
            "**【利率定价】** 宽松预期起 ➡️ **美债2年期收益率 ↓** (直线跳水) ➡️ **美债10年期收益率 ↓** (受再通胀担忧扰动，下行可能受阻)",
            "**【汇率博弈】** 美元溢价消失 ➡️ **美元指数 ↓** 🟢顺向推升🟢 **非美货币 (人民币汇率修复) ↑**",
            "**【大类资产】** 实际利率回落 + 美元贬值 ➡️ 资金寻求抗通胀实物 ➡️ **黄金 ↑** ➕ **大宗商品 (铜/油) ↑**",
            "**【股市风格】** 资金重回风险偏好 ➡️ **美股科技股/A股成长股 ↑** (拔估值) 🔴反转压制🔴 **传统银行股利差 ↓**"
        ],
        "链路置信度": [84, 82, 80, 76],
        "核心逻辑": "全球打开水龙头，流动性泛滥。资金溢出寻找高弹性收益，美元走弱直接推升以美元计价的大宗商品和避险金价。",
        "反转测试": "降息的背景是什么？如果是'纾困式紧急降息'（如应对突发衰退或流动性危机），恐慌情绪蔓延，股市和商品会先经历暴跌（现金为王），此时只有黄金和美债能避险。"
    },
    "美国非农/CPI 超预期走高": {
        "上涨(↑)": [
            "美元指数",
            "美债2年期收益率",
            "美债10年期收益率"
        ],
        "下跌(↓)": [
            "黄金",
            "美股 (尤其高估值板块)",
            "A股/港股",
            "离岸人民币"
        ],
        "传导链条": [
            "**【加息预期复燃】** 通胀粘性/就业火热 ➡️ 市场延后降息预期 ➡️ **美债2年期收益率 ↑**",
            "**【汇率与流动性】** 收益率预期走高 ➡️ **美元指数 ↑** 🔴反转压制🔴 **离岸人民币 ↓** (外资流出新兴市场预期增强)",
            "**【资产被动承压】** 强势美元 + 高利率 🔴反转压制🔴 **黄金 ↓** ➕ **高估值权益资产 (中美股市) ↓**"
        ],
        "链路置信度": [83, 80, 78],
        "核心逻辑": "经济数据过热打碎了市场的宽松幻觉，资金重新计入“Higher for Longer（更长的高息时代）”，导致美元流动性瞬间收紧。",
        "反转测试": "如果通胀走高但就业数据崩溃（即典型的“滞胀”），市场可能会忽略通胀，直接押注衰退降息，导致美元美债双杀，黄金单边暴涨。"
    },
    "长短美债收益率倒挂 (2年期 > 10年期)": {
        "上涨(↑)": [
            "高评级长久期国债",
            "黄金",
            "日元"
        ],
        "下跌(↓)": [
            "全球股市",
            "周期股",
            "原油/铜等顺周期商品"
        ],
        "传导链条": [
            "**【信贷传导】** 短端利率 > 长端利率 ➡️ 银行“借短放长”无利可图 ➡️ **实体信贷紧缩 ↓**",
            "**【宏观衰退预期】** 信用扩张受阻 ➡️ 实体投资与库存周期走弱 🔴反转压制🔴 **原油/铜等顺周期商品 ↓** ➕ **全球股市 ↓**",
            "**【避险资金流动】** 资金预判经济硬着陆 ➡️ 抢跑买入 **高评级长久期国债 ↑** ➕ **黄金/日元 ↑**"
        ],
        "链路置信度": [88, 82, 79],
        "核心逻辑": "短期资金成本高于长期投资回报，这是资本市场对未来6-18个月经济衰退最准的“报警器”。",
        "反转测试": "倒挂期间股市往往还在冲顶（最后的狂欢）。真正的暴跌往往发生在'倒挂结束，收益率曲线重新陡峭'的那一刻（确认衰退到来，美联储被迫紧急降息）。"
    },
    "中国社融/PMI 数据超预期": {
        "上涨(↑)": [
            "A股/港股顺周期板块",
            "人民币汇率",
            "工业金属 (铜/铁矿石)",
            "中国10年期国债收益率"
        ],
        "下跌(↓)": [
            "中国国债价格",
            "纯防御型高股息板块"
        ],
        "传导链条": [
            "**【宽信用兑现】** 社融改善/订单回暖 ➡️ 实体融资需求旺盛 ➡️ **中国10年期国债收益率 ↑** (债市资金流出)",
            "**【风险偏好切换】** 经济复苏预期加强 ➡️ 资金撤出 **纯防御型高股息板块 ↓** 🔄流向🔄 **A股/港股顺周期板块 ↑**",
            "**【汇率与商品】** 国内基本面筑底 ➡️ **人民币汇率 ↑** (升值) ➕ **黑色系/工业金属 (铜/铁矿石) ↑**"
        ],
        "链路置信度": [80, 77, 74],
        "核心逻辑": "政策底向市场底传导，国内经济引擎重启。资金从避险的债市和红利板块，重新杀入具有进攻弹性的权益和商品市场。",
        "反转测试": "单月脉冲不等于趋势反转。需观察核心均线支撑位是否企稳。若仅为政策刺激的短期效应，实体利润未跟上，极易形成'冲高回落'的诱多站岗盘。"
    }
}

st.subheader("推演工作台")
st.caption("阅读提示：债券收益率与债券价格通常反向变化；2年期更偏政策预期，10年期同时反映增长与通胀预期。")

mode = st.radio("选择模式", ["单场景推演", "双场景对比"], horizontal=True)
events = list(macro_rules.keys())

if mode == "单场景推演":
    indicator = st.selectbox("选择要推演的宏观触发事件：", options=events)
    confidence_offset = st.slider(
        "市场环境修正（用于微调链路置信度）",
        min_value=-20,
        max_value=20,
        value=0,
        step=5,
        help="偏乐观可上调，偏悲观可下调。这个修正不会改变方向，仅改变你对链路强弱的主观打分。"
    )

    result = macro_rules[indicator]

    st.markdown("### ⚡ 核心逻辑")
    st.info(result["核心逻辑"])

    render_direction_panel(result)

    with st.expander("🔗 查看详细传导链（进阶）", expanded=True):
        for idx, chain in enumerate(result["传导链条"]):
            score = clamp_confidence(result["链路置信度"][idx] + confidence_offset)
            st.markdown(f"{idx + 1}. {chain}")
            st.progress(score / 100, text=f"链路置信度：{score}%")

    st.markdown("### 🛡️ 交易防御系统")
    st.error(f"**⚖️ Devil's Advocate (反转测试):**\n\n{result['反转测试']}")

    single_report = build_single_report(indicator, result, confidence_offset)
    st.download_button(
        label="📄 导出本场景简报（Markdown）",
        data=single_report,
        file_name=f"宏观推演简报_{indicator}.md",
        mime="text/markdown"
    )

else:
    col_left, col_right = st.columns(2)
    with col_left:
        event_a = st.selectbox("场景A", options=events, index=0)
    with col_right:
        default_index_b = 1 if len(events) > 1 else 0
        event_b = st.selectbox("场景B", options=events, index=default_index_b)

    result_a = macro_rules[event_a]
    result_b = macro_rules[event_b]

    if event_a == event_b:
        st.warning("当前 A/B 选择相同，建议切换为不同场景进行对照。")

    st.markdown("### 🧭 对比视图")
    col_a, col_b = st.columns(2)
    with col_a:
        render_compare_card("场景A", event_a, result_a)
    with col_b:
        render_compare_card("场景B", event_b, result_b)

    a_up = set(result_a["上涨(↑)"])
    b_up = set(result_b["上涨(↑)"])
    a_down = set(result_a["下跌(↓)"])
    b_down = set(result_b["下跌(↓)"])

    st.markdown("### 🔍 交集与差异")
    st.markdown(f"**共同上涨资产**：{', '.join(sorted(a_up & b_up)) if (a_up & b_up) else '无'}")
    st.markdown(f"**共同下跌资产**：{', '.join(sorted(a_down & b_down)) if (a_down & b_down) else '无'}")
    st.markdown(f"**仅场景A上涨**：{', '.join(sorted(a_up - b_up)) if (a_up - b_up) else '无'}")
    st.markdown(f"**仅场景B上涨**：{', '.join(sorted(b_up - a_up)) if (b_up - a_up) else '无'}")

    compare_report = build_compare_report(event_a, result_a, event_b, result_b)
    st.download_button(
        label="📄 导出对比简报（Markdown）",
        data=compare_report,
        file_name=f"场景对比简报_{event_a}_VS_{event_b}.md",
        mime="text/markdown"
    )

st.markdown("---")
st.caption("🚨 纪律提醒：此罗盘仅提供宏观胜率的底层传导方向。所有的建仓决策，必须经过宏观核心数据与微观技术图形（核心均线/布林带中轨）的交叉验证，坚持在极具盈亏比的区间低吸。")