"""Compatibility hook for first-run setup.

The inherited demo recording has unresolved redistribution rights and speaks a
legacy product name. Startup must not create or refresh a profile from that
recording. Existing user profiles, including historical demo rows, remain user
data and are left untouched.
"""


def seed_sample_project() -> None:
    """Leave first-run voice profiles empty until a cleared sample is provided."""
    return None
