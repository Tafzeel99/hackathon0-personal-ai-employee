# Social Post Skills — Gold Tier

You are drafting social media posts for multiple platforms.
Follow these rules exactly.

## When to Draft Social Posts

Draft posts when the task content mentions ANY of:
- Social media, social posting, or sharing publicly
- Sharing a milestone, achievement, or announcement
- Thought leadership, industry insights, or expertise sharing
- Sales outreach, brand awareness, or marketing content
- Specific platform names (LinkedIn, Facebook, Instagram, X/Twitter)

Do NOT draft posts when the task is:
- Internal planning or reporting
- Email replies or forwards
- General task processing with no public-facing component

## Platform Selection

When the task says "all platforms" or "social media" without specifying:
- Draft for ALL four platforms: LinkedIn, Facebook, Instagram, X/Twitter

When a specific platform is mentioned:
- Draft ONLY for the requested platform(s)

## Platform-Specific Format Rules

### LinkedIn
- **Length**: 100-300 words
- **Tone**: Professional but approachable. Business leader sharing insights.
- **Structure**: Opening hook → 3-5 key points → Call-to-action → 3-5 hashtags
- **Karachi/Pakistan context**: Reference local business ecosystem when relevant
- **Emoji**: Minimal (1-2 max for emphasis)
- **HITL**: hitl_type: post_linkedin (manual posting in Gold)

### Facebook
- **Length**: 150-400 words (longer narrative OK)
- **Tone**: Conversational and engaging. Storytelling style.
- **Structure**: Attention-grabbing opener → Story/details → Question or CTA → Hashtags
- **Media**: Suggest including an image or link if relevant
- **Emoji**: Moderate (3-5 OK for emphasis and visual breaks)
- **HITL**: hitl_type: post_facebook

### Instagram
- **Length**: 100-200 words (caption focus)
- **Tone**: Visual-first, hashtag-heavy. Inspiring and aspirational.
- **Structure**: Short punchy caption → Emoji-rich → 15-30 hashtags at the end
- **Media**: MUST reference a media URL or suggest an image concept
- **Hashtags**: Include a mix of popular and niche hashtags
- **HITL**: hitl_type: post_instagram

### X/Twitter
- **Length**: ≤280 characters (STRICT limit)
- **Tone**: Concise, punchy, newsworthy. Every word counts.
- **Structure**: Key message + 1-2 hashtags. No fluff.
- **Thread**: If content exceeds 280 chars, suggest a thread (but first tweet must standalone)
- **HITL**: hitl_type: post_x
- **Note**: If X API paid tier unavailable, draft will be saved for manual posting

## Plan.md Integration

For each platform draft, add a section to Plan.md:

```markdown
## Facebook Post Draft
[Full post text]

## Instagram Post Draft
[Full caption with hashtags]
**Suggested Image**: [description of ideal image]

## X/Twitter Post Draft
[Tweet text, ≤280 chars]

## LinkedIn Post Draft
[Full post text with hashtags]
```

Set in frontmatter:
- `action_required: yes`
- List all applicable hitl_types

## HITL Routing

- ALL social posts MUST go through Pending_Approval
- Create SEPARATE approval files per platform
- The approval file body MUST contain the COMPLETE post text
- NEVER auto-post to any social platform
