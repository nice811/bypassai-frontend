import requests
import time
import json
import re
import statistics
from typing import List, Dict, Tuple

API_URL = "https://bypassai-api-production.up.railway.app/api/humanize"
HEALTH_URL = "https://bypassai-api-production.up.railway.app/"


def test_health_check() -> Dict:
    """测试 API 健康检查端点"""
    result = {"test_name": "健康检查", "passed": False, "details": "", "duration_ms": 0}
    start = time.time()
    try:
        resp = requests.get(HEALTH_URL, timeout=10)
        result["duration_ms"] = int((time.time() - start) * 1000)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                result["passed"] = True
                result["details"] = f"服务正常，响应时间 {result['duration_ms']}ms"
            else:
                result["details"] = f"返回状态异常: {data}"
        else:
            result["details"] = f"HTTP 状态码: {resp.status_code}"
    except Exception as e:
        result["details"] = f"请求失败: {str(e)}"
    return result


def test_empty_input() -> Dict:
    """测试空输入"""
    result = {"test_name": "空输入验证", "passed": False, "details": "", "duration_ms": 0}
    start = time.time()
    try:
        resp = requests.post(API_URL, json={"text": ""}, timeout=10)
        result["duration_ms"] = int((time.time() - start) * 1000)
        if resp.status_code == 422:
            result["passed"] = True
            result["details"] = f"正确返回 422 验证错误，响应时间 {result['duration_ms']}ms"
        else:
            result["details"] = f"期望 422，实际 {resp.status_code}"
    except Exception as e:
        result["details"] = f"请求失败: {str(e)}"
    return result


def test_whitespace_input() -> Dict:
    """测试空白输入"""
    result = {"test_name": "空白输入验证", "passed": False, "details": "", "duration_ms": 0}
    start = time.time()
    try:
        resp = requests.post(API_URL, json={"text": "   \n\t  "}, timeout=10)
        result["duration_ms"] = int((time.time() - start) * 1000)
        if resp.status_code == 422:
            result["passed"] = True
            result["details"] = f"正确返回 422 验证错误，响应时间 {result['duration_ms']}ms"
        else:
            result["details"] = f"期望 422，实际 {resp.status_code}"
    except Exception as e:
        result["details"] = f"请求失败: {str(e)}"
    return result


def test_missing_text_field() -> Dict:
    """测试缺少 text 字段"""
    result = {"test_name": "缺少 text 字段", "passed": False, "details": "", "duration_ms": 0}
    start = time.time()
    try:
        resp = requests.post(API_URL, json={}, timeout=10)
        result["duration_ms"] = int((time.time() - start) * 1000)
        if resp.status_code == 422:
            result["passed"] = True
            result["details"] = f"正确返回 422 验证错误，响应时间 {result['duration_ms']}ms"
        else:
            result["details"] = f"期望 422，实际 {resp.status_code}"
    except Exception as e:
        result["details"] = f"请求失败: {str(e)}"
    return result


def test_oversized_input() -> Dict:
    """测试超长输入（超过10000字符）"""
    result = {"test_name": "超长输入限制", "passed": False, "details": "", "duration_ms": 0}
    long_text = "This is a test sentence. " * 500
    start = time.time()
    try:
        resp = requests.post(API_URL, json={"text": long_text}, timeout=10)
        result["duration_ms"] = int((time.time() - start) * 1000)
        if resp.status_code in (400, 422):
            result["passed"] = True
            result["details"] = f"正确拒绝超长输入 ({len(long_text)} chars)，状态码 {resp.status_code}"
        else:
            result["details"] = f"期望 400/422，实际 {resp.status_code}"
    except Exception as e:
        result["details"] = f"请求失败: {str(e)}"
    return result


TEST_CASES = [
    {
        "name": "短文本（句子级）",
        "category": "长度测试",
        "text": "Artificial intelligence is transforming the way we work and live."
    },
    {
        "name": "中等文本（段落级）",
        "category": "长度测试",
        "text": "Machine learning algorithms have become increasingly sophisticated in recent years. These systems can now process vast amounts of data and identify patterns that would be impossible for humans to detect manually. As a result, industries across the board are adopting these technologies to improve efficiency and decision-making."
    },
    {
        "name": "长文本（文章级）",
        "category": "长度测试",
        "text": "The evolution of natural language processing has been remarkable. From early rule-based systems to today's large language models, the field has undergone multiple paradigm shifts. Modern LLMs can generate coherent text, answer complex questions, and even write code. However, concerns about AI detection have grown alongside these capabilities. Educators and publishers worry about the authenticity of written content, leading to the development of various AI detection tools. These tools analyze patterns such as sentence structure uniformity, perplexity scores, and burstiness to classify text as human or AI-generated. The cat-and-mouse game between detection and evasion continues to drive innovation on both sides."
    },
    {
        "name": "学术论文风格",
        "category": "文体测试",
        "text": "This study investigates the relationship between socioeconomic status and educational outcomes. Using a longitudinal dataset of 5,000 students, we conducted regression analyses controlling for demographic variables. The results indicate a statistically significant positive correlation between household income and standardized test scores (p < 0.001). Furthermore, we found that parental education level mediates this relationship. These findings contribute to the existing literature on educational inequality and have important implications for policy interventions aimed at reducing achievement gaps."
    },
    {
        "name": "商务邮件风格",
        "category": "文体测试",
        "text": "Dear Team, I am writing to provide an update on the Q3 project timeline. After reviewing the deliverables from last week's sprint, I am pleased to report that we are on track to meet our deadline. The marketing campaign launch is scheduled for next Monday, and the development team has completed 90% of the feature implementation. Please review the attached progress report and let me know if you have any questions. Best regards."
    },
    {
        "name": "创意写作风格",
        "category": "文体测试",
        "text": "The old library smelled of dust and forgotten stories. Sunlight streamed through cracked windows, illuminating motes of dust dancing in the air. Maria ran her fingers along the leather-bound spines, feeling the weight of centuries of human thought. Somewhere in this room, she knew, was the answer she'd been searching for. The book that would change everything."
    },
    {
        "name": "技术文档风格",
        "category": "文体测试",
        "text": "The authentication flow consists of three main steps. First, the client sends a POST request to the /api/auth endpoint with the user's credentials. The server validates the credentials and generates a JWT token with a 24-hour expiration time. Second, the client includes this token in the Authorization header for subsequent requests. Third, the server verifies the token signature and expiration before processing each request. If the token is invalid or expired, the server returns a 401 Unauthorized response."
    },
    {
        "name": "英文常用词",
        "category": "语言测试",
        "text": "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet and is commonly used for typing practice and font demonstrations."
    },
    {
        "name": "带数字和统计数据",
        "category": "内容保真测试",
        "text": "According to the 2024 industry report, global e-commerce sales reached $6.3 trillion, representing a 12.5% increase from the previous year. The top three markets were China with 35%, the United States with 22%, and the United Kingdom with 8%. Mobile commerce accounted for 72% of all online transactions, up from 68% in 2023."
    },
    {
        "name": "专业术语密集",
        "category": "内容保真测试",
        "text": "The patient presented with acute myocardial infarction accompanied by ventricular tachycardia. Electrocardiogram showed ST-segment elevation in leads V1 through V4. Troponin levels were elevated at 15.2 ng/mL. The patient underwent percutaneous coronary intervention with drug-eluting stent placement in the left anterior descending artery."
    },
    {
        "name": "超短文本（5词）",
        "category": "短文本边界测试",
        "text": "AI is changing everything."
    },
    {
        "name": "极短文本（10词）",
        "category": "短文本边界测试",
        "text": "The weather today is absolutely perfect for a picnic."
    },
    {
        "name": "边界文本（约30词）",
        "category": "短文本边界测试",
        "text": "Artificial intelligence has become an integral part of modern society. From smartphones to self-driving cars, AI technology is everywhere. The impact on daily life is profound and continues to grow rapidly."
    },
    {
        "name": "单个短语无句号",
        "category": "短文本边界测试",
        "text": "Machine learning models can sometimes produce biased results"
    }
]


import math

def calculate_perplexity(text: str) -> float:
    """简单的困惑度计算（基于字符熵的近似值）"""
    if not text:
        return 0.0
    char_counts = {}
    for c in text.lower():
        char_counts[c] = char_counts.get(c, 0) + 1
    total = len(text)
    entropy = 0.0
    for count in char_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return 2 ** entropy


def calculate_burstiness(sentence_lengths: List[int]) -> float:
    """计算句子长度的变异系数（burstiness 指标）"""
    if len(sentence_lengths) < 2:
        return 0.0
    mean_len = statistics.mean(sentence_lengths)
    if mean_len == 0:
        return 0.0
    std_len = statistics.stdev(sentence_lengths)
    return std_len / mean_len


def split_sentences(text: str) -> List[str]:
    """简单的句子分割"""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def evaluate_output(original: str, humanized: str) -> Dict:
    """评估人类化输出的质量"""
    eval_result = {
        "original_length": len(original),
        "humanized_length": len(humanized),
        "length_ratio": len(humanized) / len(original) if original else 0,
        "original_sentences": len(split_sentences(original)),
        "humanized_sentences": len(split_sentences(humanized)),
        "original_perplexity": calculate_perplexity(original),
        "humanized_perplexity": calculate_perplexity(humanized),
        "perplexity_change": 0.0,
        "original_burstiness": 0.0,
        "humanized_burstiness": 0.0,
        "burstiness_change": 0.0,
        "word_overlap_ratio": 0.0,
        "same_first_words": False,
        "passes_basic_checks": False
    }

    orig_sentences = split_sentences(original)
    hum_sentences = split_sentences(humanized)

    orig_lens = [len(s.split()) for s in orig_sentences]
    hum_lens = [len(s.split()) for s in hum_sentences]

    eval_result["original_burstiness"] = calculate_burstiness(orig_lens)
    eval_result["humanized_burstiness"] = calculate_burstiness(hum_lens)

    if eval_result["original_perplexity"] > 0:
        eval_result["perplexity_change"] = (
            (eval_result["humanized_perplexity"] - eval_result["original_perplexity"])
            / eval_result["original_perplexity"]
        )

    if eval_result["original_burstiness"] > 0:
        eval_result["burstiness_change"] = (
            (eval_result["humanized_burstiness"] - eval_result["original_burstiness"])
            / eval_result["original_burstiness"]
        )

    orig_words = set(original.lower().split())
    hum_words = set(humanized.lower().split())
    if orig_words:
        eval_result["word_overlap_ratio"] = len(orig_words & hum_words) / len(orig_words)

    eval_result["same_first_words"] = original.split()[:3] == humanized.split()[:3]

    input_word_count = len(original.split())
    is_short = input_word_count < 30
    max_ratio = 2.5 if is_short else 2.0
    min_ratio = 0.4 if is_short else 0.5

    eval_result["passes_basic_checks"] = all([
        len(humanized) > 0,
        eval_result["length_ratio"] > min_ratio,
        eval_result["length_ratio"] < max_ratio,
        not humanized.startswith(original[:50]) if len(original) > 50 else True,
        eval_result["word_overlap_ratio"] < 0.95
    ])

    return eval_result


def run_test_case(test_case: Dict) -> Dict:
    """运行单个测试用例"""
    result = {
        "test_name": test_case["name"],
        "category": test_case["category"],
        "passed": False,
        "details": "",
        "duration_ms": 0,
        "input_text": test_case["text"],
        "input_length": len(test_case["text"]),
        "output": "",
        "evaluation": {}
    }

    start = time.time()
    try:
        resp = requests.post(
            API_URL,
            json={"text": test_case["text"], "stream": False},
            timeout=120
        )
        result["duration_ms"] = int((time.time() - start) * 1000)

        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and data.get("data"):
                result["output"] = data["data"]
                result["passed"] = True
                result["details"] = f"处理成功，耗时 {result['duration_ms']}ms"
                result["evaluation"] = evaluate_output(test_case["text"], data["data"])
            else:
                result["details"] = f"API 返回失败: {data}"
        elif resp.status_code == 500:
            result["details"] = f"服务端错误 (可能是 API Key 未配置): {resp.text[:200]}"
        else:
            result["details"] = f"HTTP {resp.status_code}: {resp.text[:200]}"
    except requests.exceptions.Timeout:
        result["details"] = "请求超时（>120秒）"
    except Exception as e:
        result["details"] = f"请求失败: {str(e)}"

    return result


def generate_report(func_tests: List[Dict], content_tests: List[Dict]) -> str:
    """生成测试报告"""
    report = []
    report.append("=" * 70)
    report.append("                    BypassAI 测试报告")
    report.append("=" * 70)
    report.append("")

    report.append("【一、功能测试】")
    report.append("-" * 50)
    passed_func = sum(1 for t in func_tests if t["passed"])
    report.append(f"通过: {passed_func}/{len(func_tests)}")
    report.append("")

    for test in func_tests:
        status = "✅ PASS" if test["passed"] else "❌ FAIL"
        report.append(f"{status}  {test['test_name']}")
        report.append(f"        {test['details']}")
        report.append("")

    report.append("【二、内容测试与质量评估】")
    report.append("-" * 50)
    passed_content = sum(1 for t in content_tests if t["passed"])
    report.append(f"成功处理: {passed_content}/{len(content_tests)}")
    report.append("")

    for test in content_tests:
        status = "✅ OK" if test["passed"] else "❌ FAIL"
        report.append(f"[{test['category']}] {test['test_name']}")
        report.append(f"    状态: {status}")
        report.append(f"    耗时: {test['duration_ms']}ms")
        report.append(f"    输入长度: {test['input_length']} 字符")

        if test["passed"] and test["evaluation"]:
            ev = test["evaluation"]
            report.append(f"    输出长度: {ev['humanized_length']} 字符 (比例: {ev['length_ratio']:.2f})")
            report.append(f"    句子数: {ev['original_sentences']} → {ev['humanized_sentences']}")
            report.append(f"    困惑度变化: {ev['perplexity_change']*100:+.1f}%")
            report.append(f"    句长变异系数: {ev['original_burstiness']:.3f} → {ev['humanized_burstiness']:.3f} ({ev['burstiness_change']*100:+.1f}%)")
            report.append(f"    词汇重叠率: {ev['word_overlap_ratio']*100:.1f}%")
            report.append(f"    基本质量检查: {'通过' if ev['passes_basic_checks'] else '未通过'}")

            report.append("")
            report.append("    原文片段:")
            report.append(f"      {test['input_text'][:100]}..." if len(test.get('input_text', '')) > 100 else f"      {test.get('input_text', '')}")
            report.append("")
            report.append("    输出片段:")
            report.append(f"      {test['output'][:100]}..." if len(test['output']) > 100 else f"      {test['output']}")
        else:
            report.append(f"    详情: {test['details']}")

        report.append("")

    report.append("【三、综合评估】")
    report.append("-" * 50)

    successful = [t for t in content_tests if t["passed"] and t["evaluation"]]
    if successful:
        avg_duration = statistics.mean([t["duration_ms"] for t in successful])
        avg_perplexity_change = statistics.mean([t["evaluation"]["perplexity_change"] for t in successful])
        avg_burstiness_change = statistics.mean([t["evaluation"]["burstiness_change"] for t in successful])
        avg_overlap = statistics.mean([t["evaluation"]["word_overlap_ratio"] for t in successful])
        pass_rate = sum(1 for t in successful if t["evaluation"]["passes_basic_checks"]) / len(successful)

        report.append(f"平均响应时间: {avg_duration:.0f}ms")
        report.append(f"平均困惑度变化: {avg_perplexity_change*100:+.1f}%")
        report.append(f"平均句长变异系数变化: {avg_burstiness_change*100:+.1f}%")
        report.append(f"平均词汇重叠率: {avg_overlap*100:.1f}%")
        report.append(f"基本质量检查通过率: {pass_rate*100:.0f}%")
        report.append("")

        report.append("【评分标准说明】")
        report.append("  - 困惑度: 越高表示文本越不可预测（更像人类写作）")
        report.append("  - 句长变异系数: 越高表示句子长短变化越丰富（burstiness 越高）")
        report.append("  - 词汇重叠率: 越低表示改写程度越大，但应保留核心语义")
        report.append("  - 理想状态: 困惑度上升、句长变异系数上升、词汇重叠率适中 (30%-70%)")
    else:
        report.append("无成功的测试用例，无法生成综合评估")

    report.append("")
    report.append("=" * 70)
    report.append("                    测试结束")
    report.append("=" * 70)

    return "\n".join(report)


def main():
    print("开始运行 BypassAI 测试套件...")
    print(f"API 地址: {API_URL}")
    
    try:
        resp = requests.get(HEALTH_URL, timeout=5)
        if resp.status_code == 200:
            info = resp.json()
            print(f"模型: {info.get('model', 'N/A')}")
            print(f"Prompt 长度: {info.get('prompt_length', 'N/A')}")
    except:
        pass
    print()

    func_tests = []
    content_tests = []

    print("【功能测试】")
    func_tests.append(test_health_check())
    func_tests.append(test_empty_input())
    func_tests.append(test_whitespace_input())
    func_tests.append(test_missing_text_field())
    func_tests.append(test_oversized_input())

    for test in func_tests:
        status = "✅" if test["passed"] else "❌"
        print(f"  {status} {test['test_name']}: {test['details']}")

    print()
    print("【内容质量测试】")
    print(f"  共 {len(TEST_CASES)} 个测试用例，预计需要 10-20 分钟...")
    print()

    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"  [{i}/{len(TEST_CASES)}] 测试: {test_case['name']}...", end=" ", flush=True)
        result = run_test_case(test_case)
        result["input_text"] = test_case["text"]
        content_tests.append(result)

        if result["passed"]:
            print(f"✅ 成功 ({result['duration_ms']}ms)")
        else:
            print(f"❌ 失败")
            print(f"         原因: {result['details']}")

    print()
    print("生成测试报告...")
    print()

    report = generate_report(func_tests, content_tests)
    print(report)

    with open("test_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    detailed_results = {
        "functional_tests": func_tests,
        "content_tests": [
            {k: v for k, v in t.items() if k != "output" or True}
            for t in content_tests
        ],
        "summary": {
            "func_pass_rate": sum(1 for t in func_tests if t["passed"]) / len(func_tests),
            "content_success_rate": sum(1 for t in content_tests if t["passed"]) / len(content_tests),
        }
    }

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(detailed_results, f, ensure_ascii=False, indent=2)

    print()
    print(f"详细结果已保存到 test_results.json")
    print(f"报告已保存到 test_report.txt")


if __name__ == "__main__":
    main()
