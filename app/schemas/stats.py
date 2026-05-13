from pydantic import BaseModel


class StatsPublic(BaseModel):
    credits_applied: float  # total credits
    credits_required: int  # like base 120
    degree_progress_pct: float  # 120*100/credits_applied
    credits_remaining: float  # 120-credits_applied
    cs_credits_done: float  # creadits with CS status
    cs_credits_required: int  # like base 30 or 40 idk
    cs_credits_remaining: float  # credits_reqired - credits_done
    gpa_cumulative: (
        float  # all classes grade_points total divide by amount of those classes
    )
    gpa_cs_only: float  # same for CS classses as above
    est_graduation: str  # its like remaining credits / 6 and then add todays date + the amount of semensters
    liberal_arts_credits: float  # its like all electives i guess
    requirements: list[dict] | None = None  # CS, Liberal Arts, ets
