from pathlib import Path
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
from html import unescape
from urllib.parse import unquote
def strip_html(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text().strip() if raw_html else ""

def replace_blanks(text):
    return re.sub(r"\[.*?\]", "______", text)




# Patch the parser to manually handle matching question correct answers
def parse_qti_file_patched(manifest_path: str):
    def resolve_qti_file(base_dir, relative_path):
        file_path = base_dir / relative_path
        return file_path if file_path.exists() else base_dir / Path(relative_path).name

    manifest = Path(manifest_path)
    base_dir = manifest.parent

    # Parse manifest
    manifest_root = ET.parse(manifest).getroot()
    ns = {
        "ims": "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1"
    }
    resource_nodes = manifest_root.findall(".//ims:resource", ns)
    file_paths = [res.find("ims:file", ns).attrib["href"]
                  for res in resource_nodes if res.find("ims:file", ns) is not None]

    assessment_path = next((fp for fp in file_paths if fp.endswith(".xml") and "assessment_meta" not in fp), None)
    metadata_path = next((fp for fp in file_paths if "assessment_meta" in fp), None)

    assessment_file = resolve_qti_file(base_dir, assessment_path)
    metadata_file = resolve_qti_file(base_dir, metadata_path)

    # Parse metadata
    canvas_ns = {"canvas": "http://canvas.instructure.com/xsd/cccv1p0"}
    metadata_root = ET.parse(metadata_file).getroot()
    quiz_title = metadata_root.findtext(".//canvas:title", namespaces=canvas_ns)
    time_limit = metadata_root.findtext(".//canvas:time_limit", namespaces=canvas_ns)

    question_root = ET.parse(assessment_file).getroot()
    qti_ns = {"qti": "http://www.imsglobal.org/xsd/ims_qtiasiv1p2"}

    qti_type_map = {
        "multiple_choice_question": "Multiple Choice",
        "true_false_question": "True/False",
        "short_answer_question": "Short Answer",
        "essay_question": "Essay",
        "matching_question": "Matching",
        "fill_in_multiple_blanks_question": "Fill in the Blank",
        "fill_in_the_blank": "Fill in the Blank"
    }

    questions = []
    for item in question_root.findall(".//qti:item", qti_ns):
        meta = item.find(".//qti:qtimetadata", qti_ns)
        meta_fields = {
            field.find("qti:fieldlabel", qti_ns).text: field.find("qti:fieldentry", qti_ns).text
            for field in meta.findall("qti:qtimetadatafield", qti_ns)
        }
        raw_type = meta_fields.get("question_type", "unknown")
        question_type = qti_type_map.get(raw_type, "unknown")
        points = float(meta_fields.get("points_possible", 1.0))

        text_elem = item.find(".//qti:mattext", qti_ns)
        question_text_raw = text_elem.text if text_elem is not None else ""
        question_text_clean = strip_html(question_text_raw)


        question_data = {
            "question_text": question_text_clean,
            "type": question_type,
            "default_points": points,
            "source": "canvas_qti"
        }
        
        # 🔍 Check for image attachments
        matimage = item.find(".//qti:matimage", qti_ns)
        if matimage is not None:
            image_path = matimage.attrib.get("uri")  # e.g., "quiz_media/image1.png"
            question_data["attachment_file"] = image_path

        # 🧼 Also check inside mattext for embedded <img> tags (optional/fallback)
        mattext_elem = item.find(".//qti:mattext", qti_ns)
        if  mattext_elem is not None:
            decoded_html = unescape(mattext_elem.text or "")
            if "<img" in decoded_html:
                soup = BeautifulSoup(decoded_html, "html.parser")
                img_tag = soup.find("img")
                if img_tag and img_tag.get("src"):
                    src = img_tag["src"]
                    if src.startswith("$IMS-CC-FILEBASE$/"):
                        src = src.replace("$IMS-CC-FILEBASE$/", "")
                        src = unquote(src)
                    question_data["attachment_file"] = src

        if question_type == "Multiple Choice":
            labels = item.findall(".//qti:response_label", qti_ns)
            correct = item.find(".//qti:respcondition/qti:conditionvar/qti:varequal", qti_ns)
            correct_id = correct.text if correct is not None else ""
            options = [
                {
                    "option_text": lbl.find(".//qti:mattext", qti_ns).text,
                    "is_correct": (lbl.attrib["ident"] == correct_id)
                }
                for lbl in labels
            ]
            question_data["choices"] = options

        elif question_type == "True/False":
            correct = item.find(".//qti:respcondition/qti:conditionvar/qti:varequal", qti_ns)
            correct_id = correct.text if correct is not None else ""
            labels = {
                lbl.attrib["ident"]: lbl.find(".//qti:mattext", qti_ns).text.lower()
                for lbl in item.findall(".//qti:response_label", qti_ns)
            }
            correct_answer = labels.get(correct_id)
            question_data["true_false_answer"] = (correct_answer == "true")

        elif question_type == "Matching":
            matches = []
            for resp in item.findall(".//qti:response_lid", qti_ns):
                prompt = resp.find("./qti:material/qti:mattext", qti_ns)
                correct_id = None
                for cond in item.findall(".//qti:respcondition", qti_ns):
                    varequal = cond.find(".//qti:varequal", qti_ns)
                    if varequal is not None and varequal.attrib.get("respident") == resp.attrib["ident"]:
                        correct_id = varequal.text
                        break
                for label in resp.findall(".//qti:response_label", qti_ns):
                    match_text = label.find(".//qti:mattext", qti_ns).text
                    is_correct = label.attrib["ident"] == correct_id
                    if is_correct:
                        matches.append({
                        "prompt_text": prompt.text if prompt is not None else "",
                        "match_text": match_text
                        })

            question_data["matches"] = matches

        elif question_type == "Fill in the Blank":
            question_data["question_text"] = replace_blanks(question_text_clean)
            blanks = []
            for resp in item.findall(".//qti:response_lid", qti_ns):
                prompt = resp.find("./qti:material/qti:mattext", qti_ns)
                correct_id = None
                for cond in item.findall(".//qti:respcondition", qti_ns):
                    varequal = cond.find(".//qti:varequal", qti_ns)
                    if varequal is not None and varequal.attrib.get("respident") == resp.attrib["ident"]:
                        correct_id = varequal.text
                        break
                for label in resp.findall(".//qti:response_label", qti_ns):
                    label_text = label.find(".//qti:mattext", qti_ns).text
                    is_correct = label.attrib["ident"] == correct_id
                    blanks.append({
                        "prompt": prompt.text if prompt is not None else "",
                        "correct_text": label_text,
                        "is_correct": is_correct
                    })
            question_data["blanks"] = blanks

        questions.append(question_data)

    return {
        "quiz_title": quiz_title,
        "time_limit": int(time_limit) if time_limit else None,
        "questions": questions
    }

""""
# Run the patched parser
# Gets the full path to your current working directory (your project root)
# Step 1: Build the path to imsmanifest.xml
#base_path = os.getcwd()
#manifest_path = os.path.join(base_path, "qti_testing", "imsmanifest.xml")
manifest_path = '/Users/rodjr.stuckey/Documents/GitHub/Senior-Project/Backend/API/qti_testing/group-4-project-quiz-export-3/imsmanifest.xml'
# Step 2: Parse the file
parsed = parse_qti_file_patched(manifest_path)

# Step 3: Print the summary
print("Quiz Title:", parsed["quiz_title"])
print("Time Limit:", parsed["time_limit"])
print("Total Questions:", len(parsed["questions"]))
print("=" * 40)

# Step 4: Print each question
for i, q in enumerate(parsed["questions"], start=1):
    print(f"Question {i}:")
    print("  Type:", q["type"])
    print("  Text:", q["question_text"])
    print("  Points:", q["default_points"])
    if "choices" in q:
        print("  Choices:")
        for choice in q["choices"]:
            print(f"    - {choice['text']} (Correct: {choice['is_correct']})")
    if "true_false_answer" in q:
        print("  Answer:", "True" if q["true_false_answer"] else "False")
    if "matches" in q:
        print("  Matches:")
        for m in q["matches"]:
            print(f"    - {m['prompt']} -> {m['match']} (Correct: {m['is_correct']})")
    if "blanks" in q:
        print("  Blanks:")
        for b in q["blanks"]:
            print(f"    - Prompt: {b['prompt']}, Answer: {b['answer']} (Correct: {b['is_correct']})")
    print("-" * 40)
"""