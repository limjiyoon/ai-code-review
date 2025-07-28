"""Factory class to create prompts for AI code review."""


class PromptFactory:
    """A factory class to create prompts for AI code review."""

    @staticmethod
    def general_review_prompt() -> str:
        """Generate a general review prompt for the given code snippet."""
        return (
            "You are an AI code reviewer."
            "Your task is to review the provided code "
            "and give feedback on its quality, style, and potential improvements."
            "Review the following code snippet\n\n:"
        )
