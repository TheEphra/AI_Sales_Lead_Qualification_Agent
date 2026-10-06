def get_recommended_action(lead, score, priority):
    """
    Generate a deterministic sales action based on
    qualification score, priority, and buying signals.
    """

    demo_requested = (
        str(lead["demo_requested"]).strip().lower() == "yes"
    )

    pricing_interest = (
        str(lead["pricing_interest"]).strip().lower() == "yes"
    )

    timeline = str(lead["timeline"]).strip()

    if priority == "Hot":
        if demo_requested:
            return "Contact the lead promptly and schedule the requested demo."

        if pricing_interest:
            return "Contact the lead promptly and provide pricing with a demo option."

        return "Prioritize direct outreach and qualify the lead for a sales conversation."

    if priority == "Warm":
        if timeline == "0-3 months":
            return "Follow up soon and identify the remaining requirements before purchase."

        return "Nurture the lead and follow up with relevant product information."

    return "Add the lead to a nurture sequence and monitor future engagement."