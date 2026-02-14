# Social Summary Skills — Gold Tier

You are generating social media engagement summaries across multiple platforms.
Follow these rules exactly.

## When to Generate a Summary

Generate a social activity summary when:
- A social post has been successfully published (post-dispatch summary)
- The weekly audit runs (include social section in audit)
- Explicitly requested by the user
- On a recurring schedule (e.g., weekly with the audit)

## Data Sources

Fetch activity data from each active platform:
- **Facebook**: Posts, likes, comments, shares (via social_facebook_mcp.py --action fetch_activity)
- **Instagram**: Media posts, likes, comments (via social_instagram_mcp.py --action fetch_activity)
- **X/Twitter**: Tweets, likes, retweets (via social_x_mcp.py --action fetch_activity)
- **LinkedIn**: Manual tracking only (no API fetching in Gold)

## Metrics to Highlight

For each platform, report:
1. **Post count**: Number of posts made in the period
2. **Engagement**: Total likes, comments, shares/retweets
3. **Engagement rate**: (total engagements / total posts) where available
4. **Top post**: Highest-engagement post with brief snippet

Cross-platform aggregation:
- **Total posts across all platforms**
- **Total engagements across all platforms**
- **Most active platform** (highest engagement)
- **Least active platform** (lowest or no activity)

## Sentiment Indicators

Analyze comment content (where available) for:
- **Positive signals**: Praise, interest, leads, follow-up requests
- **Negative signals**: Complaints, criticism, spam
- **Neutral**: General reactions, shares without comment

Use simple keyword matching:
- Positive: "great", "love", "interested", "amazing", "helpful", "need this"
- Negative: "bad", "disappointed", "spam", "unfollow", "worst"
- Default to neutral if unclear

## Lead Keyword Detection

Identify potential business leads in comments:
- Keywords: "price", "cost", "quote", "interested", "contact", "DM", "email"
- Flag these as "Potential Lead" in the summary

## Summary Output Format

Write to `Briefings/Social_Summary_<date>.md`:

```markdown
---
type: social_summary
period_start: <ISO date>
period_end: <ISO date>
generated: <ISO timestamp>
---

# Social Activity Summary — [date range]

## Platform Overview

| Platform | Posts | Likes | Comments | Shares/RTs | Engagement Rate |
|----------|-------|-------|----------|------------|-----------------|
| Facebook | X     | X     | X        | X          | X%              |
| Instagram| X     | X     | X        | N/A        | X%              |
| X/Twitter| X     | X     | N/A      | X          | X%              |
| LinkedIn | (manual tracking) |  |  |  |  |

## Top Performing Content
- [Platform]: "[post snippet]" — X likes, X comments

## Sentiment Overview
- Positive: X comments
- Negative: X comments
- Neutral: X comments

## Potential Leads
- [Platform] comment by [user]: "[snippet]" — keyword: "interested"

## Recommendations
- [Data-driven suggestion based on metrics]
```

## Integration with Weekly Audit

The social summary section in the weekly audit should:
1. Reference the most recent Social_Summary file
2. Include aggregate metrics for the audit period
3. Highlight any notable trends or concerns
