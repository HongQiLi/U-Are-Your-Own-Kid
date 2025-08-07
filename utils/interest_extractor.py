# utils/interest_extractor.py
# 用户兴趣提取器 / Interest Extractor

def extract_interest_from_survey(survey_data: dict) -> list:
    """
    模拟函数：根据用户的兴趣调查问卷，提取兴趣关键词。
    Simulated function to extract interest keywords from survey data.

    参数 / Params:
        survey_data (dict): 用户问卷数据 / User's survey input

    返回 / Returns:
        list: 兴趣关键词列表 / List of interest keywords
    """
    interests = []

    # 模拟提取逻辑 / Mock rule-based extraction
    if "sports" in survey_data.get("hobbies", "").lower():
        interests.append("exercise")
    if "reading" in survey_data.get("hobbies", "").lower():
        interests.append("literature")
    if "math" in survey_data.get("favorite_subjects", "").lower():
        interests.append("problem solving")
    if "art" in survey_data.get("favorite_subjects", "").lower():
        interests.append("creativity")

    if not interests:
        interests.append("general learning")  # 默认兴趣 / Default fallback

    return interests
