# K12 Knowledge Point Taxonomy

This reference defines the hierarchical knowledge point taxonomy used by AI Wrong Question Coach. Each knowledge point has a unique `kp_id`, a `name`, `subject`, `stage` (junior/senior), and a `parent` reference.

When analyzing a wrong question, match it to the most specific knowledge point in this taxonomy. If no exact match exists, use the closest parent category and note the gap for future taxonomy expansion.

---

## Mathematics

### Junior High (初中数学)

| kp_id | Name | Parent |
|-------|------|--------|
| MATH_JH_01 | 有理数及其运算 | MATH_JH_ROOT |
| MATH_JH_02 | 整式与因式分解 | MATH_JH_ROOT |
| MATH_JH_03 | 一元一次方程 | MATH_JH_ROOT |
| MATH_JH_04 | 二元一次方程组 | MATH_JH_ROOT |
| MATH_JH_05 | 一元二次方程 | MATH_JH_ROOT |
| MATH_JH_06 | 不等式与不等式组 | MATH_JH_ROOT |
| MATH_JH_07 | 平面直角坐标系 | MATH_JH_ROOT |
| MATH_JH_08 | 一次函数 | MATH_JH_ROOT |
| MATH_JH_09 | 反比例函数 | MATH_JH_ROOT |
| MATH_JH_10 | 二次函数 | MATH_JH_ROOT |
| MATH_JH_11 | 相交线与平行线 | MATH_JH_ROOT |
| MATH_JH_12 | 三角形(全等/相似) | MATH_JH_ROOT |
| MATH_JH_13 | 勾股定理 | MATH_JH_ROOT |
| MATH_JH_14 | 四边形(平行四边形/矩形/菱形/正方形) | MATH_JH_ROOT |
| MATH_JH_15 | 圆 | MATH_JH_ROOT |
| MATH_JH_16 | 锐角三角函数 | MATH_JH_ROOT |
| MATH_JH_17 | 图形的轴对称/旋转/平移 | MATH_JH_ROOT |
| MATH_JH_18 | 统计(平均数/中位数/方差) | MATH_JH_ROOT |
| MATH_JH_19 | 概率初步 | MATH_JH_ROOT |

### Senior High (高中数学)

| kp_id | Name | Parent |
|-------|------|--------|
| MATH_SH_01 | 集合与常用逻辑用语 | MATH_SH_ROOT |
| MATH_SH_02 | 函数概念与性质(定义域/值域/单调性/奇偶性) | MATH_SH_ROOT |
| MATH_SH_03 | 基本初等函数(指数/对数/幂函数) | MATH_SH_ROOT |
| MATH_SH_04 | 三角函数 | MATH_SH_ROOT |
| MATH_SH_05 | 三角恒等变换 | MATH_SH_ROOT |
| MATH_SH_06 | 解三角形 | MATH_SH_ROOT |
| MATH_SH_07 | 数列(等差/等比/递推) | MATH_SH_ROOT |
| MATH_SH_08 | 不等式(均值/柯西/线性规划) | MATH_SH_ROOT |
| MATH_SH_09 | 平面向量 | MATH_SH_ROOT |
| MATH_SH_10 | 复数 | MATH_SH_ROOT |
| MATH_SH_11 | 立体几何 | MATH_SH_ROOT |
| MATH_SH_12 | 解析几何(直线/圆/椭圆/双曲线/抛物线) | MATH_SH_ROOT |
| MATH_SH_13 | 空间向量与立体几何 | MATH_SH_ROOT |
| MATH_SH_14 | 排列组合与二项式定理 | MATH_SH_ROOT |
| MATH_SH_15 | 概率与统计 | MATH_SH_ROOT |
| MATH_SH_16 | 导数及其应用 | MATH_SH_ROOT |
| MATH_SH_17 | 参数方程与极坐标 | MATH_SH_ROOT |

---

## Physics

### Junior High (初中物理)

| kp_id | Name | Parent |
|-------|------|--------|
| PHYS_JH_01 | 声现象 | PHYS_JH_ROOT |
| PHYS_JH_02 | 光现象(反射/折射/透镜) | PHYS_JH_ROOT |
| PHYS_JH_03 | 质量和密度 | PHYS_JH_ROOT |
| PHYS_JH_04 | 运动和力(匀速直线/惯性/二力平衡) | PHYS_JH_ROOT |
| PHYS_JH_05 | 压强(固体/液体/大气) | PHYS_JH_ROOT |
| PHYS_JH_06 | 浮力(阿基米德原理) | PHYS_JH_ROOT |
| PHYS_JH_07 | 简单机械(杠杆/滑轮/斜面) | PHYS_JH_ROOT |
| PHYS_JH_08 | 功和机械能 | PHYS_JH_ROOT |
| PHYS_JH_09 | 内能与热机 | PHYS_JH_ROOT |
| PHYS_JH_10 | 电路基础(串并联/欧姆定律) | PHYS_JH_ROOT |
| PHYS_JH_11 | 电功率与焦耳定律 | PHYS_JH_ROOT |
| PHYS_JH_12 | 电与磁(电磁铁/电动机/发电机) | PHYS_JH_ROOT |

### Senior High (高中物理)

| kp_id | Name | Parent |
|-------|------|--------|
| PHYS_SH_01 | 运动的描述(位移/速度/加速度) | PHYS_SH_ROOT |
| PHYS_SH_02 | 匀变速直线运动 | PHYS_SH_ROOT |
| PHYS_SH_03 | 相互作用与力的平衡 | PHYS_SH_ROOT |
| PHYS_SH_04 | 牛顿运动定律 | PHYS_SH_ROOT |
| PHYS_SH_05 | 曲线运动(平抛/圆周) | PHYS_SH_ROOT |
| PHYS_SH_06 | 万有引力与航天 | PHYS_SH_ROOT |
| PHYS_SH_07 | 功与功率/动能定理 | PHYS_SH_ROOT |
| PHYS_SH_08 | 机械能守恒定律 | PHYS_SH_ROOT |
| PHYS_SH_09 | 动量守恒定律 | PHYS_SH_ROOT |
| PHYS_SH_10 | 静电场(库仑定律/电势/电容) | PHYS_SH_ROOT |
| PHYS_SH_11 | 恒定电流(欧姆定律/闭合电路) | PHYS_SH_ROOT |
| PHYS_SH_12 | 磁场(安培力/洛伦兹力) | PHYS_SH_ROOT |
| PHYS_SH_13 | 电磁感应(法拉第/楞次定律) | PHYS_SH_ROOT |
| PHYS_SH_14 | 交变电流与变压器 | PHYS_SH_ROOT |
| PHYS_SH_15 | 热力学(分子动理论/气体) | PHYS_SH_ROOT |
| PHYS_SH_16 | 机械振动与机械波 | PHYS_SH_ROOT |
| PHYS_SH_17 | 光学(干涉/衍射/偏振) | PHYS_SH_ROOT |
| PHYS_SH_18 | 原子物理与量子初步 | PHYS_SH_ROOT |

---

## Chemistry

### Junior High (初中化学)

| kp_id | Name | Parent |
|-------|------|--------|
| CHEM_JH_01 | 物质的变化与性质 | CHEM_JH_ROOT |
| CHEM_JH_02 | 空气与氧气 | CHEM_JH_ROOT |
| CHEM_JH_03 | 水与溶液 | CHEM_JH_ROOT |
| CHEM_JH_04 | 碳和碳的氧化物 | CHEM_JH_ROOT |
| CHEM_JH_05 | 金属与金属材料 | CHEM_JH_ROOT |
| CHEM_JH_06 | 酸碱盐 | CHEM_JH_ROOT |
| CHEM_JH_07 | 化学方程式与计算 | CHEM_JH_ROOT |
| CHEM_JH_08 | 化学实验基础 | CHEM_JH_ROOT |

### Senior High (高中化学)

| kp_id | Name | Parent |
|-------|------|--------|
| CHEM_SH_01 | 物质的量与阿伏伽德罗常数 | CHEM_SH_ROOT |
| CHEM_SH_02 | 离子反应与氧化还原反应 | CHEM_SH_ROOT |
| CHEM_SH_03 | 金属及其化合物(钠/铝/铁) | CHEM_SH_ROOT |
| CHEM_SH_04 | 非金属及其化合物(硅/氯/硫/氮) | CHEM_SH_ROOT |
| CHEM_SH_05 | 元素周期律与化学键 | CHEM_SH_ROOT |
| CHEM_SH_06 | 化学反应与能量(热化学) | CHEM_SH_ROOT |
| CHEM_SH_07 | 化学反应速率与化学平衡 | CHEM_SH_ROOT |
| CHEM_SH_08 | 水溶液中的离子平衡 | CHEM_SH_ROOT |
| CHEM_SH_09 | 电化学(原电池/电解池) | CHEM_SH_ROOT |
| CHEM_SH_10 | 有机化学基础(烃/官能团) | CHEM_SH_ROOT |
| CHEM_SH_11 | 化学实验综合 | CHEM_SH_ROOT |
| CHEM_SH_12 | 物质结构与性质 | CHEM_SH_ROOT |

---

## Chinese Language (语文)

| kp_id | Name | Parent |
|-------|------|--------|
| CN_01 | 字音字形 | CN_ROOT |
| CN_02 | 词语/成语辨析 | CN_ROOT |
| CN_03 | 病句辨析与修改 | CN_ROOT |
| CN_04 | 文言文实词与虚词 | CN_ROOT |
| CN_05 | 文言文句式与翻译 | CN_ROOT |
| CN_06 | 古诗鉴赏(意象/手法/情感) | CN_ROOT |
| CN_07 | 现代文阅读(论述类) | CN_ROOT |
| CN_08 | 现代文阅读(文学类) | CN_ROOT |
| CN_09 | 写作(记叙文/议论文) | CN_ROOT |
| CN_10 | 语言表达与运用 | CN_ROOT |
| CN_11 | 名著阅读与文学常识 | CN_ROOT |

---

## English (英语)

| kp_id | Name | Parent |
|-------|------|--------|
| EN_01 | 时态(一般/进行/完成/完成进行) | EN_ROOT |
| EN_02 | 被动语态 | EN_ROOT |
| EN_03 | 情态动词 | EN_ROOT |
| EN_04 | 虚拟语气 | EN_ROOT |
| EN_05 | 非谓语动词(不定式/分词/动名词) | EN_ROOT |
| EN_06 | 从句(定从/状从/名从) | EN_ROOT |
| EN_07 | 主谓一致 | EN_ROOT |
| EN_08 | 冠词/介词/代词 | EN_ROOT |
| EN_09 | 完形填空策略 | EN_ROOT |
| EN_10 | 阅读理解(细节/推理/主旨/词义) | EN_ROOT |
| EN_11 | 写作(书信/议论文/续写) | EN_ROOT |
| EN_12 | 听力理解 | EN_ROOT |

---

## Usage in Analysis

When the skill analyzes a wrong question:

1. Identify the subject from the question content
2. Determine stage (junior/senior) from context or user input
3. Match to the most specific `kp_id` in this taxonomy
4. If a question spans multiple knowledge points, list them in order of relevance
5. Use `kp_id` for tracking error frequency per knowledge point
