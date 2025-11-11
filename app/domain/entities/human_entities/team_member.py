from uuid import UUID


class TeamMember():
    def __init__(self, team_id: UUID, student_id: UUID, role: str, study_group: str):
        self.team_id = team_id
        self.student_id = student_id
        self.role = role
        self.study_group = study_group