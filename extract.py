import re
import json

def parse_tiku(text):
    """解析题库文本，返回题目列表（字典格式）"""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = text.split('\n')

    questions = []
    current_chapter = ""
    current_question = None
    current_option = None      # 当前正在收集的选项字母
    in_options = False         # 是否已进入选项区域

    # 各匹配规则
    re_chapter = re.compile(r'^\s*第[一二三四五六七八九十百]+章\s*$')
    re_question_start = re.compile(r'^\s*(\d+)[.．、]\s*(.*)')
    re_option_start = re.compile(r'^\s*([A-Z])[.．、]\s*(.*)')
    re_answer = re.compile(r'^\s*答案：\s*([A-Za-z])\s*$')
    re_page_number = re.compile(r'^\s*\d+\s*$')   # 独立数字视为页码，忽略

    def save_question():
        """存储当前构建完成的题目，并重置状态"""
        nonlocal current_question, current_option, in_options
        if current_question and current_question.get('options') and current_question.get('answer'):
            questions.append(current_question)
        current_question = None
        current_option = None
        in_options = False

    for line in lines:
        # 忽略纯空行和纯页码行
        if not line.strip() or re_page_number.match(line):
            continue

        # 章节标题
        if re_chapter.match(line):
            save_question()
            current_chapter = line.strip()
            continue

        # 答案行（如：答案：D）
        ans_match = re_answer.match(line)
        if ans_match and current_question is not None:
            current_question['answer'] = ans_match.group(1).upper()
            save_question()
            continue

        # 题目开头（如：1．题干内容）
        q_start = re_question_start.match(line)
        if q_start:
            save_question()
            num = q_start.group(1)
            rest = q_start.group(2).strip()
            current_question = {
                "chapter": current_chapter,
                "id": num,
                "question": rest,
                "options": {},
                "answer": None
            }
            in_options = False
            current_option = None
            continue

        # 如果当前正在构建一道题
        if current_question is not None:
            # 选项开头（如：A．政治控制）
            opt_start = re_option_start.match(line)
            if opt_start:
                in_options = True
                opt_letter = opt_start.group(1).upper()
                opt_text = opt_start.group(2).strip()
                current_question['options'][opt_letter] = opt_text
                current_option = opt_letter
                continue

            # 追加到当前选项（若在选项区域）或题干（否则）
            if in_options and current_option is not None:
                # 选项内容跨行，追加
                current_question['options'][current_option] += ' ' + line.strip()
            else:
                # 题干跨行
                current_question['question'] += ' ' + line.strip()

    # 处理文件末尾可能残留的题目
    save_question()

    return questions


if __name__ == "__main__":
    # 根据你保存的文件名，这里直接读取“近代史题库.txt”
    input_filename = "近代史题库.txt"
    output_filename = "近代史题库.json"

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_filename}，请确认文件名和路径。")
        exit(1)

    result = parse_tiku(raw_text)

    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"完成！从《{input_filename}》中共提取 {len(result)} 道题目，")
    print(f"已保存至 {output_filename}")