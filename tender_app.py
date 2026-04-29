import streamlit as st
import pandas as pd
import math

# --- 页面配置 ---
st.set_page_config(page_title="物业投标报价决策系统 V5.0", layout="wide")

# --- 侧边栏：全局战略设置 ---
with st.sidebar:
    st.title("🏗️ 项目战略配置")

    # 1. 业态选择 (逻辑分流的核心)
    project_type = st.radio("Step 1: 选择物业业态", ["居民住宅小区", "公共建筑 (办公/学校/机关)"])

    st.markdown("---")
    st.subheader("Step 2: 薪酬标准设定 (综合成本)")
    st.caption("含工资、社保、福利、工服等所有人力开支")

    # 定义三档薪酬标准，方便一键切换
    salary_level = st.select_slider("选择薪酬档次", options=["低配(基础版)", "中配(标准版)", "高配(标杆版)"])

    # 根据档次预设工资 (用户可微调)
    if salary_level == "低配(基础版)":
        std_mgr, std_cs, std_sec, std_clean, std_eng, std_kitchen = 7000, 4000, 3800, 2800, 4500, 4200
    elif salary_level == "中配(标准版)":
        std_mgr, std_cs, std_sec, std_clean, std_eng, std_kitchen = 10000, 5500, 4500, 3200, 5500, 5000
    else:  # 高配
        std_mgr, std_cs, std_sec, std_clean, std_eng, std_kitchen = 15000, 7000, 6000, 4000, 7000, 6200

    # 允许用户覆盖预设
    with st.expander("微调各类工种综合月薪", expanded=False):
        s_mgr = st.number_input("项目经理/主管", value=std_mgr)
        s_cs = st.number_input("客服/会服/前台", value=std_cs)
        s_sec = st.number_input("秩序维护 (安保)", value=std_sec)
        s_clean = st.number_input("环境保洁", value=std_clean)
        s_eng = st.number_input("工程维修", value=std_eng)
        s_kitchen = st.number_input("餐饮/厨务人员", value=std_kitchen)

# --- 主标题 ---
st.title(f"📊 {project_type} - 投标报价与利润测算（驱动因子版）")
st.markdown("---")

# ==========================================
# 模块一：项目基本盘 (根据业态不同，输入项不同)
# ==========================================
col_base1, col_base2 = st.columns(2)

households = 0
meeting_rooms = 0
has_canteen = False

with col_base1:
    st.subheader("1. 规模指标")
    total_area = st.number_input("总建筑面积 (m²)", value=50000.0, min_value=0.0)

    if project_type == "居民住宅小区":
        households = st.number_input("总户数 (户)", value=600, min_value=0)
        is_old = st.checkbox("是否为老旧小区 (>10年)?", value=True)
        repair_factor = 1.5 if is_old else 0.8
    else:
        meeting_rooms = st.number_input("会议室/多功能厅数量 (间)", value=5, min_value=0)
        has_canteen = st.checkbox("是否包含食堂/餐饮服务?", value=False)
        is_old = st.checkbox("是否为老旧建筑群 (>10年)?", value=False)
        repair_factor = 0.8

with col_base2:
    st.subheader("2. 环境与设备指标")
    green_area = st.number_input("绿化面积 (m²)", value=5000.0, min_value=0.0)
    water_area = st.number_input("水景/水体面积 (m²)", value=200.0, min_value=0.0)
    elevator_count = st.number_input("电梯数量 (台)", value=4, min_value=0)
    st.caption("电梯数量将用于“广告收入”和“电梯维保费”测算。")

    st.info("行业参考：住宅绿化养护常见 0.5–1.0 元/㎡·月，水体运维 3–5 元/㎡·月。")

# ==========================================
# 模块二：收入模型 (按业态分流 & 多经细分)
# ==========================================
st.markdown("---")
st.subheader("💰 收入测算（主营 + 车位 + 广告/其他）")

income_total = 0.0
income_desc = ""

# 各收入分项，便于后续生成“经营测算全表”
inc_basic = 0.0
inc_parking_rent = 0.0
inc_parking_mgmt = 0.0
inc_adv = 0.0
inc_other = 0.0

bid_mode = None
percent = 0.0

if project_type == "居民住宅小区":
    # 1. 物业费收入
    with st.expander("1）物业费收入测算", expanded=True):
        fee_price = st.number_input("拟投标物业费单价 (元/㎡·月)", value=2.0, min_value=0.0)
        collection_rate = st.slider("预估收缴率 (%)", 50, 100, 85) / 100
        st.caption("参考：普通住宅项目收缴率 85%–95%；老旧小区可适当保守。")
        inc_basic = total_area * fee_price * collection_rate
        st.caption(f"物业费月收入 ≈ {total_area:.0f}㎡ × {fee_price:.2f}元 × 收缴率{collection_rate*100:.1f}% ≈ {inc_basic:,.0f} 元/月")

    # 2. 车位收入（自持租金 + 已售管理费）
    with st.expander("2）车位/停车收入测算", expanded=True):
        st.caption("公式：自持车位 × 月租金 + 已售车位 × 车位管理费。建议区分地面/地下。")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            ground_total = st.number_input("地面车位总数 (个)", value=50, min_value=0)
            ground_self = st.number_input("其中自持可出租车位 (个)", value=min(30, ground_total), min_value=0, max_value=ground_total)
            ground_sold = st.number_input("其中已售私家车位 (个)", value=ground_total - ground_self, min_value=0, max_value=ground_total)
            rent_ground = st.number_input("地面自持车位月租金 (元/车位/月)", value=200.0, min_value=0.0)
        with col_p2:
            underground_total = st.number_input("地下车位总数 (个)", value=100, min_value=0)
            underground_self = st.number_input("其中自持可出租车位 (个)", value=min(60, underground_total), min_value=0, max_value=underground_total)
            underground_sold = st.number_input("其中已售私家车位 (个)", value=underground_total - underground_self, min_value=0, max_value=underground_total)
            rent_underground = st.number_input("地下自持车位月租金 (元/车位/月)", value=300.0, min_value=0.0)

        mgmt_fee = st.number_input("已售私家车位管理费 (元/车位/月)", value=50.0, min_value=0.0)

        self_parking_income = ground_self * rent_ground + underground_self * rent_underground
        sold_parking_count = ground_sold + underground_sold
        sold_parking_income = sold_parking_count * mgmt_fee

        inc_parking_rent = self_parking_income
        inc_parking_mgmt = sold_parking_income

        st.caption(
            f"自持车位租金：{ground_self + underground_self}个 × 对应租金 ≈ {self_parking_income:,.0f} 元/月；"
            f"已售车位管理费：{sold_parking_count}个 × {mgmt_fee:.0f}元 ≈ {sold_parking_income:,.0f} 元/月。"
        )

    # 3. 广告、电梯与其他经营
    with st.expander("3）广告、电梯及其他经营收入", expanded=False):
        st.caption("电梯广告一般按“单梯月度单价 × 电梯数量”测算，可根据市场行情调整。")
        adv_unit = st.number_input("单梯广告月度收入 (元/台/月)", value=500.0, min_value=0.0)
        inc_adv = elevator_count * adv_unit

        inc_other = st.number_input("其他经营收入 (元/月)", value=0.0, min_value=0.0)
        st.caption("示例：社区团购佣金、便民服务摊位、水电代收服务费等。")

    income_total = inc_basic + inc_parking_rent + inc_parking_mgmt + inc_adv + inc_other
    income_desc = "物业费 + 车位收入 + 广告/其他"

else:  # 公共建筑
    col_inc1, col_inc2 = st.columns(2)
    with col_inc1:
        bid_mode = st.radio("报价模式", ["包干制 (总价包死)", "酬金制 (实报实销+酬金)"])
    with col_inc2:
        if bid_mode == "包干制 (总价包死)":
            contract_sum = st.number_input("甲方招标控制价/上限 (元/年)", value=1983500.0, min_value=0.0)
            income_total = contract_sum / 12
            income_desc = "月度合同包干价 = 年度上限 / 12"
        else:
            percent = st.number_input("期望酬金比例（% ，基于成本）", value=8.0, min_value=0.0)
            st.warning("酬金制：先在下方测算各项成本，再按“硬成本 × (1 + 酬金比例)”反推合同收入。")
            income_desc = "成本 + 酬金（下方成本测算完成后反推）"

    # 公共建筑通常无停车对外经营，这里只保留一个可选其他经营口径
    with st.expander("可选：其他经营收入（如会议场地对外出租等）", expanded=False):
        inc_other = st.number_input("其他经营收入 (元/月)", value=0.0, min_value=0.0)
        income_total += inc_other

# ==========================================
# 模块三：成本测算（由驱动因素反推金额）
# ==========================================
st.markdown("---")
st.subheader("🛠️ 成本分解（人力 + 设备维保 + 能耗 + 风险）")

# -----------------------------
# 1. 人力成本：由岗位/面积驱动
# -----------------------------
with st.expander("1）人力成本配置（按驱动因素测算）", expanded=True):
    st.caption("核心思路：人数 = 驱动因子（岗位数/面积等）× 班次/效率，人力成本 = 人数 × 综合月薪。")

    # 经理 / 客服 / 工程 推荐值
    if project_type == "居民住宅小区":
        rec_mgr = 1
        rec_cs = max(1, math.ceil(households / 300))
        rec_eng = max(1, math.ceil(total_area / 20000))
    else:
        rec_mgr = 1
        rec_cs = max(2, meeting_rooms)  # 简化：每间会议室配 1 人会服
        rec_eng = max(1, math.ceil(total_area / 15000) + 1)

    col_hr1, col_hr2, col_hr3 = st.columns(3)
    with col_hr1:
        st.caption(f"项目经理（建议 {rec_mgr} 人）")
        n_mgr = st.number_input("项目经理人数", value=rec_mgr, min_value=0)
        cost_mgr = n_mgr * s_mgr
    with col_hr2:
        st.caption(f"客服/会服/前台（建议 ≥ {rec_cs} 人）")
        n_cs = st.number_input("客服/会服人数", value=rec_cs, min_value=0)
        cost_cs = n_cs * s_cs
    with col_hr3:
        st.caption(f"工程维修（建议 ≥ {rec_eng} 人）")
        n_eng = st.number_input("工程维修人数", value=rec_eng, min_value=0)
        cost_eng = n_eng * s_eng

    st.markdown("---")
    st.markdown("###### 安保岗位测算（门岗/巡逻岗 × 班次 × 单班人数）")
    sec_c1, sec_c2, sec_c3 = st.columns(3)
    with sec_c1:
        sec_posts = st.number_input("门岗/巡逻岗数量 (个岗位)", value=4, min_value=0)
    with sec_c2:
        sec_shifts = st.number_input("每岗班次（几班倒）", value=3, min_value=1)
        st.caption("提示：住宅/校园安保通常为“三班倒”，每班 8 小时。")
    with sec_c3:
        sec_per_shift = st.number_input("单班在岗人数 (人)", value=1, min_value=1)

    n_sec = sec_posts * sec_shifts * sec_per_shift
    cost_sec = n_sec * s_sec
    st.caption(f"安保编制 = {sec_posts} 岗 × {sec_shifts} 班 × {sec_per_shift} 人/班 ≈ **{n_sec} 人**，月人力成本 ≈ {cost_sec:,.0f} 元。")

    st.markdown("###### 保洁岗位测算（按人均清洁面积反推人数）")
    clean_c1, clean_c2 = st.columns(2)
    with clean_c1:
        eff_clean = st.number_input("人均清洁面积效能 (㎡/人)", value=3000.0, min_value=1.0)
        st.caption("参考：普通办公/住宅 2500–3500 ㎡/人；高标准、高频保洁可下调到 2000 ㎡/人以下。")
    with clean_c2:
        extra_clean = st.number_input("额外机动保洁人数 (人)", value=0, min_value=0)

    base_clean_num = math.ceil(total_area / eff_clean) if eff_clean > 0 else 0
    n_clean = base_clean_num + extra_clean
    cost_clean = n_clean * s_clean
    st.caption(
        f"基础保洁人数 ≈ ceiling({total_area:.0f}㎡ / {eff_clean:.0f}㎡) = {base_clean_num} 人，加机动 {extra_clean} 人，"
        f"合计 **{n_clean} 人**，月人力成本 ≈ {cost_clean:,.0f} 元。"
    )

    # 公共建筑：餐饮/食堂模块
    cost_kitchen = 0.0
    n_kitchen_total = 0
    if project_type == "公共建筑 (办公/学校/机关)" and has_canteen:
        st.markdown("---")
        st.markdown("###### 餐饮/食堂人力配置（仅公共建筑）")
        st.caption("根据食堂出餐量和营业时间配置厨师/帮厨/服务员。")
        kc1, kc2, kc3, kc4 = st.columns(4)
        with kc1:
            n_chef = st.number_input("厨师人数", value=2, min_value=0)
        with kc2:
            n_assistant = st.number_input("帮厨人数", value=2, min_value=0)
        with kc3:
            n_waiter = st.number_input("服务员人数", value=3, min_value=0)
        with kc4:
            s_kitchen_effective = st.number_input("餐饮岗位平均综合月薪 (元/人/月)", value=s_kitchen, min_value=0.0)

        n_kitchen_total = n_chef + n_assistant + n_waiter
        cost_kitchen = n_kitchen_total * s_kitchen_effective
        st.caption(f"食堂总编制 {n_kitchen_total} 人，月人力成本 ≈ {cost_kitchen:,.0f} 元。")

total_staff_num = n_mgr + n_cs + n_sec + n_clean + n_eng + (n_kitchen_total if 'n_kitchen_total' in locals() else 0)
total_labor_cost = cost_mgr + cost_cs + cost_sec + cost_clean + cost_eng + (cost_kitchen if 'cost_kitchen' in locals() else 0.0)

# -----------------------------
# 2. 设施设备与能耗成本
# -----------------------------
with st.expander("2）设施设备与能耗成本", expanded=True):
    col_op1, col_op2 = st.columns(2)

    with col_op1:
        st.markdown("###### 环境维护成本")
        green_unit = st.number_input("绿化养护单价 (元/㎡·月)", value=0.6, min_value=0.0)
        water_unit = st.number_input("水体运行单价 (元/㎡·月)", value=4.0, min_value=0.0)
        env_consumables = st.number_input("保洁耗材/垃圾清运 (元/月)", value=3000.0, min_value=0.0)

        green_cost = green_area * green_unit
        water_cost = water_area * water_unit
        cost_env = green_cost + water_cost + env_consumables
        st.caption(
            f"绿化养护 ≈ {green_area:.0f}㎡ × {green_unit:.2f}元 + 水体 {water_area:.0f}㎡ × {water_unit:.2f}元 "
            f"+ 耗材/清运 ≈ **{cost_env:,.0f} 元/月**。"
        )

    with col_op2:
        st.markdown("###### 设备维保与能耗成本")
        st.caption("电梯维保 = 电梯数量 × 单台维保月费；能耗可由“每平米能耗预估”反推。")
        elev_unit = st.number_input("单台电梯维保费 (元/台/月)", value=800.0, min_value=0.0)
        elevator_maint_cost = elevator_count * elev_unit

        energy_ref = st.number_input("每平米能耗预估 (元/㎡·月)", value=0.8, min_value=0.0)
        est_energy = energy_ref * total_area
        energy_public = st.number_input("公区能耗实际测算值 (元/月)", value=float(est_energy), min_value=0.0)
        st.caption(
            f"参考能耗 ≈ {total_area:.0f}㎡ × {energy_ref:.2f}元 ≈ {est_energy:,.0f} 元/月，可与实际填报值对比调整。"
        )

        base_maintain = total_area * 0.5 * repair_factor  # 简化：按面积与老旧程度估算基础维保
        cost_eng_mat = base_maintain + elevator_maint_cost + energy_public
        st.caption(f"工程与能耗小计（含一般设施维保、电梯维保、公区能耗）≈ **{cost_eng_mat:,.0f} 元/月**。")

core_cost_before_admin_tax = total_labor_cost + cost_env + cost_eng_mat

# -----------------------------
# 3. 管理费与税金
# -----------------------------
with st.expander("3）总部管理费与税金", expanded=True):
    admin_ratio = st.slider("总部管理费占收入比例 (%)", 2, 10, 5) / 100
    tax_ratio = st.number_input("增值税及附加综合税率 (%)", value=6.0, min_value=0.0) / 100
    st.caption("参考：一般纳税人增值税 6% 左右，附加税通常并入综合税率统一测算。")

    # 酬金制：根据硬成本反推收入（不含管理费与税金）
    if project_type == "公共建筑 (办公/学校/机关)" and bid_mode == "酬金制 (实报实销+酬金)":
        base_for_fee = core_cost_before_admin_tax
        income_total = base_for_fee * (1 + percent / 100)
        income_desc = f"按硬成本 × (1 + {percent:.1f}%) 反推月度合同收入"

    cost_admin = income_total * admin_ratio
    cost_tax = income_total * tax_ratio

    st.caption(
        f"总部管理费 ≈ 收入 × {admin_ratio*100:.1f}% = {cost_admin:,.0f} 元/月；"
        f"税金 ≈ 收入 × {tax_ratio*100:.1f}% = {cost_tax:,.0f} 元/月。"
    )

cost_before_risk = core_cost_before_admin_tax + cost_admin + cost_tax

# -----------------------------
# 4. 项目基础条件评估与风险预备费
# -----------------------------
with st.expander("4）项目基础条件评估与风险预备费", expanded=True):
    st.caption("若项目条件较差（老旧 + 维修基金不足 + 设备完好率低），建议预留 3%–5% 风险不可预见费。")
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        has_fund = st.radio("维修基金是否充足？", ["充足", "一般", "基本没有"], index=1)
    with col_r2:
        equip_status = st.selectbox("设备设施完好率评估", ["高（≥98%）", "中（95%–98%）", "低（<95%）"], index=1)
    with col_r3:
        st.caption("风险系数由系统根据上述条件自动判断，严重情况上浮至 5%。")

    # 简单规则：累加风险点，最高不超过 5%
    risk_ratio = 0.0
    if is_old:
        risk_ratio += 0.02
    if has_fund == "基本没有":
        risk_ratio += 0.02
    elif has_fund == "一般":
        risk_ratio += 0.01

    if equip_status == "中（95%–98%）":
        risk_ratio += 0.01
    elif equip_status == "低（<95%）":
        risk_ratio += 0.03

    # 阈值与上限
    if risk_ratio < 0.03:
        risk_ratio = 0.0  # 轻微问题不计提风险费
    risk_ratio = min(risk_ratio, 0.05)

    risk_fee = cost_before_risk * risk_ratio
    if risk_ratio > 0:
        st.info(f"已按当前项目条件建议计提风险不可预见费：约为总成本的 {risk_ratio*100:.1f}%。")
        st.caption(f"风险不可预见费 ≈ (人力 + 环境 + 维保 + 管理费 + 税金) × {risk_ratio*100:.1f}% ≈ {risk_fee:,.0f} 元/月。")
    else:
        st.caption("项目基础条件较好，当前未计提额外风险不可预见费。")

total_cost = cost_before_risk + risk_fee

# ==========================================
# 模块四：决策总览 & 《项目经营测算全表》
# ==========================================
st.markdown("---")
st.header("📊 最终决策账本")

profit = income_total - total_cost
margin = (profit / income_total * 100) if income_total > 0 else 0.0

# 1. 核心数据卡片
k1, k2, k3, k4 = st.columns(4)
k1.metric("投标总报价 / 月度总收入", f"¥{income_total:,.0f}", income_desc)
k2.metric("预估总成本（含风险费）", f"¥{total_cost:,.0f}", f"人力占比 {total_labor_cost / total_cost * 100:.1f}%" if total_cost > 0 else "")
k3.metric("月度净利润", f"¥{profit:,.0f}", f"净利率 {margin:.1f}%")

# 风险提示逻辑（结合利润与项目条件）
risk_msg = "正常"
if income_total <= 0:
    risk_msg = "⚠️ 收入未正确设置，请先完成收入测算。"
elif project_type == "居民住宅小区":
    if "collection_rate" in locals() and collection_rate < 0.8:
        risk_msg = "⚠️ 高风险：收缴率偏低，现金流压力较大。"
    elif margin < 5:
        risk_msg = "⚠️ 利润过低：建议优化人力配置或调高物业费单价。"
else:
    if margin < 8:
        risk_msg = "⚠️ 公建项目毛利偏低：需关注资金占用及考核扣款风险。"

if "risk_ratio" in locals() and risk_ratio > 0:
    risk_msg += " 已计提风险不可预见费，请在投标方案中重点说明。"

k4.metric("风险评估", risk_msg)

if "risk_ratio" in locals() and risk_ratio > 0:
    st.warning(
        f"本项目条件一般/偏差，系统已自动在总成本中加入约 {risk_ratio*100:.1f}% 的“风险不可预见费”，"
        f"金额约 {risk_fee:,.0f} 元/月，请在投标说明中单独列示该项。"
    )

# 2. 《项目经营测算全表》生成
st.subheader("📑 《项目经营测算全表》")

rows = []


def add_row(category: str, item: str, basis: str, monthly: float):
    annual = monthly * 12
    share = (monthly / income_total * 100) if income_total > 0 else 0.0
    rows.append(
        {
            "收支大类": category,
            "细分项目": item,
            "计算依据/备注": basis,
            "月度金额": round(monthly, 2),
            "年度金额": round(annual, 2),
            "占比(%)": round(share, 2),
        }
    )


# 收入部分
if project_type == "居民住宅小区":
    add_row(
        "主营收入",
        "物业费收入",
        f"{total_area:.0f}㎡ × {fee_price:.2f}元/㎡·月 × 收缴率{collection_rate*100:.1f}%",
        inc_basic,
    )
    add_row(
        "多经收入",
        "车位租赁收入（自持车位）",
        f"地面自持{ground_self}个 × {rent_ground:.0f}元 + 地下自持{underground_self}个 × {rent_underground:.0f}元",
        inc_parking_rent,
    )
    add_row(
        "多经收入",
        "车位管理费收入（已售车位）",
        f"已售车位 {sold_parking_count} 个 × {mgmt_fee:.0f}元/车位/月",
        inc_parking_mgmt,
    )
    add_row(
        "多经收入",
        "广告/电梯收入",
        f"电梯 {elevator_count} 台 × 单梯广告 {adv_unit:.0f} 元/台/月",
        inc_adv,
    )
    add_row(
        "多经收入",
        "其他经营收入",
        "社区经营及其他增值服务",
        inc_other,
    )
else:
    main_income_month = income_total - inc_other
    if bid_mode == "包干制 (总价包死)":
        add_row(
            "主营收入",
            "物业服务合同收入（包干制）",
            f"年度上限 {contract_sum:,.0f} 元 ÷ 12",
            main_income_month,
        )
    else:
        add_row(
            "主营收入",
            "物业服务合同收入（酬金制）",
            f"硬成本 {core_cost_before_admin_tax:,.0f} 元/月 × (1 + {percent:.1f}%)",
            main_income_month,
        )
    add_row(
        "多经收入",
        "其他经营收入",
        "会议场地、配套服务等对外经营",
        inc_other,
    )

# 人力成本
add_row("人力成本", "项目管理人员工资", f"{n_mgr} 人 × {s_mgr:.0f} 元/人/月", cost_mgr)
add_row("人力成本", "客服/会服/前台工资", f"{n_cs} 人 × {s_cs:.0f} 元/人/月", cost_cs)
add_row("人力成本", "安保工资", f"{n_sec} 人 × {s_sec:.0f} 元/人/月", cost_sec)
add_row("人力成本", "保洁工资", f"{n_clean} 人 × {s_clean:.0f} 元/人/月", cost_clean)
add_row("人力成本", "工程维修人员工资", f"{n_eng} 人 × {s_eng:.0f} 元/人/月", cost_eng)
if "cost_kitchen" in locals() and cost_kitchen > 0:
    add_row("人力成本", "餐饮/食堂人员工资", f"{n_kitchen_total} 人 × {s_kitchen:.0f} 元/人/月", cost_kitchen)

# 环境与能耗
add_row(
    "环境维护成本",
    "绿化及水体养护",
    f"绿化{green_area:.0f}㎡ × {green_unit:.2f}元 + 水体{water_area:.0f}㎡ × {water_unit:.2f}元",
    green_cost + water_cost,
)
add_row(
    "环境维护成本",
    "保洁耗材及垃圾清运",
    "按月度经验值测算",
    env_consumables,
)
add_row(
    "能源费",
    "公区能耗",
    f"参考能耗 {energy_ref:.2f} 元/㎡·月，对应估算 {est_energy:,.0f} 元，实际填报 {energy_public:,.0f} 元/月",
    energy_public,
)

# 维保费
add_row(
    "维保费",
    "电梯维保费",
    f"电梯 {elevator_count} 台 × {elev_unit:.0f} 元/台/月",
    elevator_maint_cost,
)
add_row(
    "维保费",
    "一般设施与房屋维保",
    f"按建筑面积 {total_area:.0f}㎡ × 0.5元 × 老旧系数{repair_factor:.2f}",
    base_maintain,
)

# 管理费用与税金
add_row(
    "管理费用",
    "总部管理费",
    f"按收入 × {admin_ratio*100:.1f}%",
    cost_admin,
)
add_row(
    "税金",
    "增值税及附加",
    f"按收入 × {tax_ratio*100:.1f}%",
    cost_tax,
)

# 风险预备费
if "risk_fee" in locals() and risk_fee > 0:
    add_row(
        "风险准备金",
        "风险不可预见费",
        f"按上述成本小计 × {risk_ratio*100:.1f}%",
        risk_fee,
    )

# 利润
add_row(
    "利润",
    "月度净利润",
    "月度收入合计 − 总成本（含风险费）",
    profit,
)

df_full = pd.DataFrame(rows)
st.dataframe(df_full)

csv_full = df_full.to_csv(index=False).encode("utf-8-sig")
st.download_button("📥 导出《项目经营测算全表》CSV", csv_full, "project_full_measurement.csv", "text/csv")

import streamlit as st
import pandas as pd
import math

# --- 页面配置 ---
st.set_page_config(page_title="物业投标报价决策系统 V4.0", layout="wide")

# --- 侧边栏：全局战略设置 ---
with st.sidebar:
    st.title("🏗️ 项目战略配置")
    
    # 1. 业态选择 (逻辑分流的核心)
    project_type = st.radio("Step 1: 选择物业业态", ["居民住宅小区", "公共建筑 (办公/学校/机关)"])
    
    st.markdown("---")
    st.subheader("Step 2: 薪酬标准设定 (综合成本)")
    st.caption("含工资、社保、福利、工服等所有人力开支")
    
    # 定义三档薪酬标准，方便一键切换
    salary_level = st.select_slider("选择薪酬档次", options=["低配(基础版)", "中配(标准版)", "高配(标杆版)"])
    
    # 根据档次预设工资 (用户可微调)
    if salary_level == "低配(基础版)":
        std_mgr, std_cs, std_sec, std_clean, std_eng = 7000, 4000, 3800, 2800, 4500
    elif salary_level == "中配(标准版)":
        std_mgr, std_cs, std_sec, std_clean, std_eng = 10000, 5500, 4500, 3200, 5500
    else: # 高配
        std_mgr, std_cs, std_sec, std_clean, std_eng = 15000, 7000, 6000, 4000, 7000
    
    # 允许用户覆盖预设
    with st.expander("微调各类工种综合月薪", expanded=False):
        s_mgr = st.number_input("项目经理/主管", value=std_mgr)
        s_cs = st.number_input("客服/会议/前台", value=std_cs)
        s_sec = st.number_input("秩序维护 (保安)", value=std_sec)
        s_clean = st.number_input("环境保洁", value=std_clean)
        s_eng = st.number_input("工程维修", value=std_eng)

# --- 主标题 ---
st.title(f"📊 {project_type} - 投标报价与利润测算")
st.markdown("---")

# ==========================================
# 模块一：项目基本盘 (根据业态不同，输入项不同)
# ==========================================
col_base1, col_base2 = st.columns(2)

with col_base1:
    st.subheader("1. 规模指标")
    total_area = st.number_input("总建筑面积 (m²)", value=50000.0)
    
    if project_type == "居民住宅小区":
        households = st.number_input("总户数 (户)", value=600)
        is_old = st.checkbox("是否为老旧小区 (>10年)?", value=True)
        # 老旧小区维修成本系数
        repair_factor = 1.5 if is_old else 0.5
    else:
        # 公建关注具体功能区
        meeting_rooms = st.number_input("会议室/VIP接待室 (间)", value=5)
        has_canteen = st.checkbox("是否包含食堂服务?", value=False)
        repair_factor = 0.8 # 公建通常设备较新或有维保商

with col_base2:
    st.subheader("2. 环境与特殊指标")
    green_area = st.number_input("绿化面积 (m²)", value=5000.0)
    water_area = st.number_input("水景/水体面积 (m²)", value=200.0)
    
    # 自动计算环境成本单价建议
    st.info(f"💡 建议：绿化养护按 0.5-1.0元/m²，水体按 3-5元/m² 测算")

# ==========================================
# 模块二：收入模型 (分流)
# ==========================================
st.markdown("---")
st.subheader("💰 收入测算")

col_inc1, col_inc2 = st.columns(2)

income_total = 0
income_desc = ""

if project_type == "居民住宅小区":
    with col_inc1:
        fee_price = st.number_input("拟投标物业费 (元/m²/月)", value=2.0)
        collection_rate = st.slider("预估收缴率 (%)", 50, 100, 85) / 100
        inc_basic = total_area * fee_price * collection_rate
    with col_inc2:
        inc_parking = st.number_input("车位/多经月度净收益 (元)", value=10000.0)
    
    income_total = inc_basic + inc_parking
    income_desc = f"物业费({collection_rate*100}%) + 多经"

else: # 公共建筑
    with col_inc1:
        bid_mode = st.radio("报价模式", ["包干制 (总价包死)", "酬金制 (实报实销+酬金)"])
    with col_inc2:
        if bid_mode == "包干制 (总价包死)":
            contract_sum = st.number_input("甲方招标控制价/上限 (元/年)", value=2000000.0)
            income_total = contract_sum / 12
            income_desc = "月度合同包干价"
        else:
            percent = st.number_input("期望酬金比例 (%)", value=8.0)
            st.warning("酬金制需先算出成本，最后叠加利润。请先看下方成本。")
            income_desc = "成本 + 酬金"

# ==========================================
# 模块三：精细化成本 (核心逻辑)
# ==========================================
st.markdown("---")
st.subheader("🛠️ 成本分解 (人+事+物)")

# 1. 人力成本 (根据面积智能推荐 + 手工修正)
st.markdown("##### 1. 人力编制 (Smart HR)")

# --- 智能推荐算法 ---
if project_type == "居民住宅小区":
    rec_sec = math.ceil(total_area / 10000 * 1.2)  # 住宅保安少
    rec_clean = math.ceil(total_area / 4000)
    rec_cs = math.ceil(households / 300)
    rec_eng = math.ceil(total_area / 20000)
else: # 公建
    rec_sec = math.ceil(total_area / 5000 * 1.5)   # 公建保安多(形象岗)
    rec_clean = math.ceil(total_area / 2500)       # 公建保洁频次高
    rec_cs = meeting_rooms * 1 + 2                 # 会服人员
    rec_eng = math.ceil(total_area / 15000) + 1    # 需更多技工

# --- 输入表格 ---
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.caption("项目经理")
    n_mgr = st.number_input("人数", value=1, key="n_mgr")
    cost_mgr = n_mgr * s_mgr
with c2:
    st.caption(f"客服/会服 (推{rec_cs})")
    n_cs = st.number_input("人数", value=rec_cs, key="n_cs")
    cost_cs = n_cs * s_cs
with c3:
    st.caption(f"秩序维护 (推{rec_sec})")
    n_sec = st.number_input("人数", value=rec_sec, key="n_sec")
    cost_sec = n_sec * s_sec
with c4:
    st.caption(f"环境保洁 (推{rec_clean})")
    n_clean = st.number_input("人数", value=rec_clean, key="n_clean")
    cost_clean = n_clean * s_clean
with c5:
    st.caption(f"工程维修 (推{rec_eng})")
    n_eng = st.number_input("人数", value=rec_eng, key="n_eng")
    cost_eng = n_eng * s_eng

total_staff_num = n_mgr + n_cs + n_sec + n_clean + n_eng
total_labor_cost = cost_mgr + cost_cs + cost_sec + cost_clean + cost_eng

# 2. 专项成本 (绿化、水体、维保)
st.markdown("##### 2. 专项运营成本")
col_op1, col_op2, col_op3 = st.columns(3)

with col_op1:
    # 绿化水体计算
    green_cost = green_area * st.number_input("绿化养护单价 (元/m²/月)", value=0.6)
    water_cost = water_area * st.number_input("水体运行单价 (元/m²/月)", value=4.0)
    env_consumables = st.number_input("保洁耗材/垃圾清运 (元/月)", value=3000.0)
    cost_env = green_cost + water_cost + env_consumables
    st.caption(f"环境小计: {cost_env:.0f}")

with col_op2:
    # 工程维保计算
    base_maintain = total_area * 0.5 * repair_factor # 基础维保
    elevator_cost = st.number_input("电梯/消防委外维保 (元/月)", value=5000.0)
    energy_public = st.number_input("公区能耗 (元/月)", value=12000.0)
    cost_eng_mat = base_maintain + elevator_cost + energy_public
    st.caption(f"工程能耗小计: {cost_eng_mat:.0f}")

with col_op3:
    # 行政与税金
    admin_ratio = st.slider("总部管理费占比 (%)", 2, 10, 5) / 100
    tax_ratio = 0.06 # 6% 增值税
    
    # 动态计算基数
    if project_type == "公共建筑 (办公/学校/机关)" and bid_mode == "酬金制 (实报实销+酬金)":
         # 酬金制下，收入待定，先算硬成本
         base_for_fee = total_labor_cost + cost_env + cost_eng_mat
         income_total = base_for_fee * (1 + percent/100) # 反推收入
    
    cost_admin = income_total * admin_ratio
    cost_tax = income_total * tax_ratio
    st.caption(f"税金+管理费: {cost_admin + cost_tax:.0f}")

# 总成本
total_cost = total_labor_cost + cost_env + cost_eng_mat + cost_admin + cost_tax

# ==========================================
# 模块四：决策大屏
# ==========================================
st.markdown("---")
st.header("📊 最终决策账本")

profit = income_total - total_cost
margin = (profit / income_total * 100) if income_total > 0 else 0

# 1. 核心数据卡片
k1, k2, k3, k4 = st.columns(4)
k1.metric("投标总报价/总收入", f"¥{income_total:,.0f}", income_desc)
k2.metric("预估总成本", f"¥{total_cost:,.0f}", f"人力占比 {total_labor_cost/total_cost*100:.1f}%")
k3.metric("月度净利润", f"¥{profit:,.0f}", f"净利率 {margin:.1f}%")

# 风险提示逻辑
risk_msg = "正常"
if project_type == "居民住宅小区":
    if collection_rate < 0.8:
        risk_msg = "⚠️ 高风险：收缴率设定过低，现金流可能断裂"
    elif margin < 5:
        risk_msg = "⚠️ 风险：利润微薄，抗风险能力差，建议裁减编制"
else:
    if margin < 8:
        risk_msg = "⚠️ 风险：公建项目通常需要垫资，低毛利可能导致资金占用成本过高"

k4.metric("风险评估", risk_msg)

# 2. 报价清单生成 (模拟标书格式)
st.subheader("📑 招标文件-报价分项表生成")

quote_data = {
    "费用项目": [
        "一、人员费用 (工资福利)", 
        "二、公共能耗费", 
        "三、绿化及环境养护费", 
        "四、设施设备日常维保费", 
        "五、办公及行政管理费", 
        "六、法定税金 (6%)", 
        "七、企业利润", 
        "【总计报价】"
    ],
    "月度金额 (元)": [
        f"{total_labor_cost:,.2f}",
        f"{energy_public:,.2f}",
        f"{cost_env:,.2f}",
        f"{base_maintain + elevator_cost:,.2f}",
        f"{cost_admin:,.2f}",
        f"{cost_tax:,.2f}",
        f"{profit:,.2f}",
        f"**{income_total:,.2f}**"
    ],
    "占比": [
        f"{total_labor_cost/income_total*100:.1f}%",
        f"{energy_public/income_total*100:.1f}%",
        f"{cost_env/income_total*100:.1f}%",
        f"{(base_maintain + elevator_cost)/income_total*100:.1f}%",
        f"{cost_admin/income_total*100:.1f}%",
        f"{cost_tax/income_total*100:.1f}%",
        f"{margin:.1f}%",
        "100%"
    ]
}

df_quote = pd.DataFrame(quote_data)
st.table(df_quote)

# 下载功能
csv = df_quote.to_csv(index=False).encode('utf-8-sig')
st.download_button("📥 导出报价单 (Excel/CSV)", csv, "bidding_quote.csv", "text/csv")
