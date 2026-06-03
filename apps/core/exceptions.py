"""
Custom exception classes
"""


class SkillForgeException(Exception):
    """Base exception for SkillForge application"""
    pass


class RoadmapGenerationError(SkillForgeException):
    """Raised when roadmap generation fails"""
    pass


class CalendarIntegrationError(SkillForgeException):
    """Raised when Google Calendar integration fails"""
    pass


class GitHubCreationError(SkillForgeException):
    """Raised when GitHub repository creation fails"""
    pass
