# models/user_profile.py
# 用户画像 / User Profile

from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from datetime import date

# 一个时间段（每天可有多个）/ a daily time block
class TimeBlock(BaseModel):
    start: str = Field(..., regex=r"^\d{2}:\d{2}$")  # "HH:MM"
    end: str   = Field(..., regex=r"^\d{2}:\d{2}$")  # "HH:MM"

# 每周模板：周一到周日任意天、每一天若干时间段
# weekly template: weekday -> list of blocks
class WeeklyTemplate(BaseModel):
    weekly: Dict[str, List[TimeBlock]] = Field(
        default_factory=dict,
        description='e.g. {"Mon":[{"start":"19:00","end":"20:00"}], "Sat":[{"start":"10:00","end":"12:00"}]}'
    )

# 单日覆盖：某一天临时改动（放假/生病/加练）
# one-off overrides for specific dates
class DateOverride(BaseModel):
    day: date
    blocks: List[TimeBlock] = Field(default_factory=list)  # 为空=那天不可用

# 可用时间总体结构：时区 + 周模板 + 单日覆盖
class Availability(BaseModel):
    timezone: str = "local"                      # 可按需存 Olson ID，如 "America/Los_Angeles"
    template: WeeklyTemplate = Field(default_factory=WeeklyTemplate)
    overrides: List[DateOverride] = Field(default_factory=list)

    # 便捷方法：展开某天的最终可用时间段
    def resolve_for(self, day: date) -> List[TimeBlock]:
        wd = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][day.weekday()]
        base = self.template.weekly.get(wd, [])
        for ov in self.overrides:
            if ov.day == day:
                return ov.blocks
        return base

# 用户画像：把 availability 换成上面的灵活结构
class UserProfile(BaseModel):
    user_id: str
    name: str = ""
    survey: str = ""
    availability: Availability = Field(default_factory=Availability)

    # —— 向后兼容：允许旧格式 {"Mon": 60, ...} 作为额外输入（可选）——
    legacy_minutes: Optional[Dict[str, int]] = None

    @validator("availability", always=True)
    def _merge_legacy(cls, v, values):
        """
        如果请求里带了 legacy_minutes，就自动转换为 1 个时间段。
        例如 {"Mon":60} → {"Mon":[{"start":"19:00","end":"20:00"}]}
        这里为了演示，统一从 19:00 开始；前端最终会用拖拽改具体时间。
        """
        legacy = values.get("legacy_minutes")
        if legacy:
            weekly: Dict[str, List[TimeBlock]] = {}
            for wd, mins in legacy.items():
                if mins <= 0:
                    continue
                # 简单把分钟数塞成一个块：19:00 起，持续 mins 分钟
                h, m = 19, 0
                end_h = h + (m + mins)//60
                end_m = (m + mins)%60
                weekly[wd] = [TimeBlock(start=f"{h:02d}:{m:02d}", end=f"{end_h:02d}:{end_m:02d}")]
            v.template.weekly.update(weekly)
        return v
