from enum import Enum


class ProjectTeamStatus(str, Enum):
    """Статус участия команды в проекте"""
    
    ACTIVE = "ACTIVE"        # Активно участвует
    COMPLETED = "COMPLETED"  # Участие завершено (проект завершен)
    WITHDRAWN = "WITHDRAWN"  # Команда отозвана из проекта
    PENDING = "PENDING"      # Ожидает подтверждения