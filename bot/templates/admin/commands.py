from ...db.models.models import ReferralLinks

hello_admin_msg = 'Привет, админ!'

async def message_ref_links() -> str:

    all_links = await ReferralLinks.all()

    if not all_links:
        return "❌ Реферальные ссылки отсутствуют."

    lines = ["📎 Список всех реферальных ссылок:\n"]
    for link in all_links:
        lines.append(f"🔗 <code>{link.referral_link}</code> — 👥 {link.number_users} пользователей")

    return "\n".join(lines)