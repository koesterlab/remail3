"""Service for file permission operations."""


class PermissionService:
    """Service for handling file permission conversions and operations."""

    @staticmethod
    def parse_permission_string(perm_str: str) -> int:
        """
        Convert a permission string (e.g., 'rwxrw-r--') to octal integer.

        Args:
            perm_str: Permission string in rwx format (9 characters)

        Returns:
            Octal permission value

        Raises:
            ValueError: If string is not 9 characters
        """
        if len(perm_str) != 9:
            raise ValueError(f"Permission string must be 9 characters, got {len(perm_str)}")

        val = 0
        for group_idx in range(3):  # owner, group, others
            for perm_idx in range(3):  # read, write, execute
                char_idx = group_idx * 3 + perm_idx
                if perm_str[char_idx] != "-":
                    # Calculate permission value: group multiplier (64, 8, 1) * permission value (4, 2, 1)
                    group_multiplier = 8 ** (2 - group_idx)
                    perm_value = 2 ** (2 - perm_idx)
                    val += group_multiplier * perm_value

        return val
