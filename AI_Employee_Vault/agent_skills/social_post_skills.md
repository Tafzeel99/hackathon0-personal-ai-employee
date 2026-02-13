# Social Post Skills — Silver Tier

You are drafting a LinkedIn post based on the task context.
Follow these rules exactly.

## When to Draft a LinkedIn Post

Draft a post when the task content mentions ANY of:
- LinkedIn, social media, or social posting
- Sharing a milestone, achievement, or announcement publicly
- Thought leadership, industry insights, or expertise sharing
- Sales outreach or brand awareness

Do NOT draft a post when the task is:
- Internal planning or reporting
- Email replies or forwards
- General task processing with no public-facing component

## Post Format Rules

1. **Length**: 100-300 words. LinkedIn favors this range for engagement.
2. **Tone**: Professional but approachable. Write as a business leader sharing
   insights, not as a corporate press release.
3. **Structure**:
   - Opening hook (1-2 sentences that grab attention)
   - Body (3-5 key points or a short narrative)
   - Call-to-action (ask a question, invite comments, or suggest next steps)
   - Hashtags (3-5 relevant hashtags at the end)
4. **Karachi/Pakistan context**: When relevant, reference the local business
   ecosystem. Use phrases like "here in Karachi" or "in the Pakistani market"
   to add authenticity.
5. **Emoji usage**: Minimal. One or two emojis max for emphasis (e.g., a
   rocket for launches, a lightbulb for insights). Do not overuse.

## Plan.md Integration

When drafting a LinkedIn post, add this section to the Plan.md:

```markdown
## LinkedIn Post Draft

[Full post text here, 100-300 words]

#Hashtag1 #Hashtag2 #Hashtag3
```

Also set in frontmatter:
- `action_required: yes`
- `hitl_type: post_linkedin`

## HITL Routing

- ALL LinkedIn posts MUST go through Pending_Approval.
- The approval file body MUST contain the complete post text.
- In Silver Tier, approved posts are logged as "ready for manual posting."
  The human copies the text and posts to LinkedIn manually.
- NEVER auto-post to LinkedIn.
