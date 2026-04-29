import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="V7.1 标书精算台 (标书拆解+潮汐优化全能版)", layout="wide")

# ==========================================
# 数据加载器：优先从 JSON 配置文件读取，回退到硬编码默认值
# ==========================================
def load_bid_data(json_path="bid_extracted_data.json"):
    """加载招标分析数据。优先读取 JSON 配置文件，不存在则使用内置默认值。"""
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return _get_default_data()

def _get_default_data():
    """内置默认数据（成都博物馆），作为无 JSON 配置时的回退。"""
    return {
    "project_info": {
        "name": "成都博物馆2025年度物业管理服务采购项目",
        "type": "公共文化建筑（国家一级博物馆）",
        "total_area": 65000.0,
        "max_budget_per_year": 0
    },
    "staff_requirements": [
        {
            "role": "项目经理",
            "bid_req_count": 1,
            "actual_plan_count": 1,
            "suggested_salary": 8000,
            "note": "男性年龄<55岁/女性<45岁；本科及以上学历；非住宅物业项目经理5年以上经验；工作日9:00-17:00，法定节假日2人在岗（13天×2人），无休息日加班费"
        },
        {
            "role": "项目副经理",
            "bid_req_count": 1,
            "actual_plan_count": 1,
            "suggested_salary": 7000,
            "note": "年龄<45岁；大专及以上学历；非住宅物业项目副经理3年以上经验；工作日9:00-17:00，法定节假日2人在岗（13天×2人），无休息日加班费"
        },
        {
            "role": "工程主管",
            "bid_req_count": 1,
            "actual_plan_count": 1,
            "suggested_salary": 7500,
            "note": "年龄<45岁；大专及以上学历；非住宅物业工程主管3年以上经验；须持特种设备安全管理人员证（代号A）、高压电工作业证、低压电工作业证；工作日9:00-17:00"
        },
        {
            "role": "保洁及绿化主管",
            "bid_req_count": 1,
            "actual_plan_count": 1,
            "suggested_salary": 6500,
            "note": "年龄<45岁；大专及以上学历；非住宅物业保洁或绿化主管3年以上经验；工作日9:00-17:00"
        },
        {
            "role": "综合维修（水电气）及电梯运行、消防维保配合",
            "bid_req_count": 6,
            "actual_plan_count": 6,
            "suggested_salary": 6000,
            "note": "男性<55岁/女性<50岁；均持低压电工作业证，至少2人持特种设备安全管理证（代号T）；非住宅物业综合维修3年以上经验；24小时三班倒（白班2人/中班1人/夜班1人），法定节假日4人在岗（13天×4人），无休息日加班费"
        },
        {
            "role": "配电班",
            "bid_req_count": 8,
            "actual_plan_count": 8,
            "suggested_salary": 6500,
            "note": "男性<55岁/女性<50岁；均持高压电工作业证和低压电工作业证；非住宅物业电力维修3年以上经验；24小时四班三运转（每班2岗），法定节假日6人在岗（13天×6人），休息日加班：每周2人×8小时"
        },
        {
            "role": "空调班",
            "bid_req_count": 4,
            "actual_plan_count": 4,
            "suggested_salary": 6000,
            "note": "男性<55岁/女性<50岁；均持制冷与空调作业证；非住宅物业空调维修3年以上经验；24小时四班三运转（每班1岗），法定节假日3人在岗（13天×3人），休息日加班：每周1人×8小时"
        },
        {
            "role": "保洁员",
            "bid_req_count": 24,
            "actual_plan_count": 24,
            "suggested_salary": 3800,
            "note": "男性<55岁/女性<50岁；1年以上本岗位经验；两班倒（7:00-15:00白班12人，15:00-21:30晚班6人），夜班另有说明（文件第（四）节保洁分布表有夜班5人）；法定节假日20人在岗（13天×20人），无休息日加班费；文件第（四）节保洁分布合计18人为白+夜班驻守说明，招标硬性人数以第六节总人数24人为准"
        },
        {
            "role": "绿化景观养护维护服务",
            "bid_req_count": 1,
            "actual_plan_count": 1,
            "suggested_salary": 4500,
            "note": "男性<55岁/女性<50岁；3年以上绿化相关工作经验；8小时工作制，每周不超过40小时；法定节假日1人在岗（13天×1人），无休息日加班费"
        }
    ],
    "default_fixed_costs": {
        "便民设施及耗材（含燃气系统维保及维修一年）": 522000,
        "专业吸污疏通（12次/年）": 36000,
        "抽油烟机及烟道清洗（2次/年）": 6000,
        "直饮机保养（年）": 8000,
        "工装服装费（47人×4季×2套）": 94000,
        "供应商设备工具费（年摊销）": 50000
    },
    "extraction_notes": [
        {
            "field": "project_info.max_budget_per_year",
            "source_quote": "招标文件未明示预算上限金额，仅在不可竞争费用处注明'此项费用52.2万元为不可竞争费用'",
            "rule": "文件未披露采购最高限价/年度预算总额，故填0。投标人需根据成本测算自行报价，可参考不可竞争费用52.2万元加上人工及其他可竞争费用估算总价",
            "confidence": 0.1
        },
        {
            "field": "project_info.total_area",
            "source_quote": "总建筑面积约65000平方米……需保洁面积（㎡）约65000",
            "rule": "文件明确建筑总面积与保洁面积均为65000㎡，直接采用",
            "confidence": 0.98
        },
        {
            "field": "staff_requirements[保洁员].bid_req_count",
            "source_quote": "保洁部……保洁员 24……总计 47",
            "rule": "第六节人员需求表明确保洁员24人；第四节保洁分布表合计18人为白班驻守+夜班驻守人数（非全员），以第六节人员总表为准",
            "confidence": 0.95
        },
        {
            "field": "staff_requirements[各岗位].suggested_salary",
            "source_quote": "基本工资不低于《四川省人民政府关于调整全省最低工资标准的通知》（川府规〔2024〕4号）规定的最低工资标准（第一档）",
            "rule": "文件仅规定最低工资下限，未提供各岗位具体薪资。依据成都市同类文博物业项目市场行情保守估算：管理岗6500-8000元/月，持证技术岗6000-6500元/月，保洁员3800元/月，绿化1人4500元/月。置信度中等",
            "confidence": 0.6
        },
        {
            "field": "default_fixed_costs.专业吸污疏通",
            "source_quote": "专业吸污疏通一年12次",
            "rule": "文件明确次数12次/年，单价按成都市专业吸污疏通市场均价约3000元/次估算，年合计36000元",
            "confidence": 0.55
        },
        {
            "field": "default_fixed_costs.抽油烟机及烟道清洗",
            "source_quote": "抽油烟机和油烟管道每年专业深度清洗2次",
            "rule": "文件明确2次/年，单价按市场均价约3000元/次估算，年合计6000元",
            "confidence": 0.55
        },
        {
            "field": "default_fixed_costs.直饮机保养",
            "source_quote": "直饮机保养一年，供应商应对该服务内容进行报价",
            "rule": "文件共有直饮机约24台（商用反渗透2台+YT-3K 5台+FY-2W 2台+400SKQ 5台+SG-2000 10台），按市场均价约330元/台/年估算，年合计约8000元（保守）",
            "confidence": 0.5
        },
        {
            "field": "default_fixed_costs.工装服装费",
            "source_quote": "春装、夏装、秋装、冬装各两套确保着装统一、整洁干净",
            "rule": "47人×4季×2套，按均价250元/套估算，合计94000元",
            "confidence": 0.55
        },
        {
            "field": "default_fixed_costs.供应商设备工具费",
            "source_quote": "完成本项目服务工作所需的工机具、设备、消耗品均由中标供应商提供",
            "rule": "文件列出清洗车、洗地机、抛光机等49类设备，按采购成本年摊销（3年摊销）保守估算约5万元/年",
            "confidence": 0.4
        }
    ]
}

# ==========================================
# 加载数据：优先读取 bid_extracted_data.json，不存在则使用内置默认值
# ==========================================
ai_extracted_data = load_bid_data()

st.title(f"🤖 深度解析与精算大屏: {ai_extracted_data['project_info']['name']}")
st.markdown("---")

# ---------------- 模块零：标书原始盘面拆解 ----------------
st.header("📋 标书核心盘面拆解")
col1, col2, col3 = st.columns(3)
col1.metric("标的业态", ai_extracted_data['project_info']['type'])
col2.metric("计费总面积 (㎡)", f"{ai_extracted_data['project_info']['total_area']:,.1f}")
col3.metric("大盘总预算/年", f"¥ {ai_extracted_data['project_info']['max_budget_per_year']:,.0f}")

st.markdown("---")

# ---------------- 模块一：大盘与常态人力对比 ----------------
st.header("1️⃣ 核心人力底盘 (标书定编 vs 实际排班)")
welfare_rate = st.sidebar.slider("全局综合人工系数 (底线1.35防社保暴雷)", 1.0, 1.6, 1.35, step=0.01)
budget_from_file = ai_extracted_data['project_info']['max_budget_per_year']
use_manual_budget = st.sidebar.toggle("手动录入年度预算", value=(budget_from_file == 0))
if use_manual_budget:
    budget_for_calc = st.sidebar.number_input(
        "年度预算录入 (元)",
        min_value=0,
        value=int(budget_from_file) if budget_from_file > 0 else 5000000,
        step=10000
    )
else:
    budget_for_calc = budget_from_file

total_labor_cost_month = 0
total_bid_headcount = 0
total_actual_headcount = 0
optimization_savings_month = 0

st.markdown("**岗位明细拆解：**")
for staff in ai_extracted_data["staff_requirements"]:
    c_role, c_bid, c_actual, c_sal, c_cost = st.columns([1.5, 1, 1, 1, 1.5])
    with c_role:
        st.write(f"**{staff['role']}**\n\n*{staff['note']}*")
    with c_bid:
        st.markdown(f"标书死要求: `{staff['bid_req_count']} 人`")
        total_bid_headcount += staff['bid_req_count']
    with c_actual:
        actual_num = st.number_input("基础排班", value=staff['actual_plan_count'], key=f"n_{staff['role']}")
        total_actual_headcount += actual_num
    with c_sal:
        actual_sal = st.number_input("实发月薪", value=staff['suggested_salary'], step=100, key=f"s_{staff['role']}")
    with c_cost:
        m_cost = actual_num * actual_sal * welfare_rate
        st.write(f"实耗: ¥ {m_cost:,.0f}/月")
        total_labor_cost_month += m_cost
        optimization_savings_month += (staff['bid_req_count'] - actual_num) * actual_sal * welfare_rate

annual_base_labor_cost = total_labor_cost_month * 12

st.warning(f"🟡 **编制差异汇总**：标书硬性要求总编制 **{total_bid_headcount}** 人，您当前实际基础排班 **{total_actual_headcount}** 人。通过常态排班优化，每月为您节省人工成本 **¥ {optimization_savings_month:,.0f}**，年化增收 **¥ {optimization_savings_month * 12:,.0f}**。")

# ---------------- 模块二：博物馆专属潮汐降本 ----------------
st.markdown("---")
st.header("🌊 2️⃣ 专家支招：博物馆专属“潮汐与闭馆日”降本台")
st.info("💡 **实操提示**：除了常态少排人，博物馆的隐性降本窗口在于：**1. 利用周一闭馆日狂压加班费；2. 在 3-6月、9-11月的淡季工作日大幅替换低价兼职保洁和保安。**")

col_t1, col_t2 = st.columns(2)
with col_t1:
    st.write("**窗口一：工作日淡季“偷天换日”**")
    off_peak_months = st.slider("全年淡季时长 (预估几个月散客极少)", 0, 8, 5)
    off_peak_headcount_reduction = st.number_input("淡季期间可再抽走的【人头数】(转兼职/保洁轮休)", value=4, step=1)
    off_peak_savings_year = off_peak_months * off_peak_headcount_reduction * 3200 * welfare_rate
    st.success(f"通过淡季压编，每年额外增收: **¥ {off_peak_savings_year:,.0f}**")

with col_t2:
    st.write("**窗口二：周一闭馆日“极限调休”**")
    monday_overtime_savings_month = st.number_input("利用周一闭馆强制调休，每月少发的【预估加班费及替岗费】", value=5000, step=1000)
    monday_savings_year = monday_overtime_savings_month * 12
    st.success(f"通过闭馆日压榨加班费，每年额外增收: **¥ {monday_savings_year:,.0f}**")

final_annual_labor_cost = annual_base_labor_cost - off_peak_savings_year - monday_savings_year

# ---------------- 模块三：固定成本市场询价 ----------------
st.markdown("---")
st.header("📞 3️⃣ 刚性外包与耗材 (市场询价调节台)")
st.write("在此输入你通过本地供应商实际询价拿到底价，挤干标书隐藏成本的水分。")

actual_fixed_costs = {}
c1, c2 = st.columns(2)
for i, (cost_name, default_val) in enumerate(ai_extracted_data["default_fixed_costs"].items()):
    with c1 if i % 2 == 0 else c2:
        actual_val = st.number_input(f"{cost_name}", value=default_val, step=1000)
        actual_fixed_costs[cost_name] = actual_val

total_fixed_cost_year = sum(actual_fixed_costs.values())
tax_rate = st.sidebar.number_input("增值税及附加税率 (%)", value=6.0) / 100
risk_fund = st.number_input("年度不可预见风险预备金 (应对扣款及300元免赔坑)", value=100000, step=10000)

# ---------------- 模块四：最终决算 ----------------
st.markdown("---")
st.header("📊 4️⃣ 极度精算后的最终利润")

annual_tax = budget_for_calc * tax_rate
total_cost_year = final_annual_labor_cost + total_fixed_cost_year + risk_fund + annual_tax
net_profit_year = budget_for_calc - total_cost_year

pc1, pc2, pc3, pc4 = st.columns(4)
pc1.metric("大盘总收入", f"¥ {budget_for_calc:,.0f}")
pc2.metric("实操硬成本(含税)", f"¥ {total_cost_year:,.0f}")
pc3.metric("动态调控降本总额", f"¥ {(optimization_savings_month * 12) + off_peak_savings_year + monday_savings_year:,.0f}")

if net_profit_year > 0 and budget_for_calc > 0:
    pc4.metric("💰 极致榨取后净利", f"¥ {net_profit_year:,.0f}", f"净利率 {(net_profit_year / budget_for_calc) * 100:.1f}%")
else:
    pc4.metric("💀 极致榨取后净利", f"¥ {net_profit_year:,.0f}", "依然亏损或预算未录入！", delta_color="inverse")
