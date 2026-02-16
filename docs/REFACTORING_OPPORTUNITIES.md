# Refactoring & Improvement Opportunities

Prioritized list of opportunities to refactor and improve the TFN CTV / music_beta codebase.

---

## High priority (security & correctness)

### 1. **Password handling (security)**

- **Where:** `music_beta/views.py` (signup, login_view), `music_beta/models.User` (extends AbstractUser).
- **Issue:** Signup stores plaintext password; login compares `user.password == password`. Django’s AbstractUser expects hashed passwords via `set_password()` / `check_password()`.
- **Change:** In signup use `User.objects.create(...)` then `user.set_password(password)` and `user.save()`. In login use `user.check_password(password)` instead of `user.password == password`. Update `generate_fake_data` and tests to use `set_password()` where they create users.

### 2. **ClientCampaignForm M2M not saved**

- **Where:** `music_beta/views.py` → `create_campaign`.
- **Issue:** Form has `tracks` (ManyToMany). Code does `form.save(commit=False)`, sets `campaign.user`, then `campaign.save()` but never `form.save_m2m()`, so selected tracks are never saved.
- **Change:** After `campaign.save()` call `form.save_m2m()`.

### 3. **CSRF exemptions**

- **Where:** `@csrf_exempt` on `signup`, `upload_ad_campaign`, `search`, `get_pexels_images`, `update_play_count`.
- **Issue:** Disables CSRF for those views; increases risk of cross-site request forgery.
- **Change:** Prefer sending CSRF token from frontend (e.g. header or form field) and remove `@csrf_exempt` where possible. If some endpoints must stay exempt (e.g. external webhooks), document why and restrict by method/origin.

---

## Medium priority (maintainability)

### 4. **Repeated “session user” logic**

- **Where:** `client_dashboard`, `campaign_detail`, `create_campaign`, `edit_campaign`, `add_to_cart`, `remove_from_cart` in `music_beta/views.py`.
- **Issue:** Same pattern repeated: check `user_id` in session, `User.objects.get(id=user_id)`, handle `DoesNotExist`, optionally require `user_type == 'client'`.
- **Change:** Extract a helper (e.g. `get_session_user(request, require_client=False)`) that returns `(user, None)` or `(None, redirect_response)`. Use it in all six views to remove duplication and centralize redirect messages.

### 5. **Settings: email and dead code**

- **Where:** `tfn_ctv/settings.py`.
- **Issue:** `EMAIL_BACKEND` and `DEFAULT_FROM_EMAIL` set twice (console backend then SMTP), so SMTP overwrites. `_CONF = {}` is unused.
- **Change:** Use a single block: e.g. if `DEBUG` use console backend and a dev `DEFAULT_FROM_EMAIL`; else use SMTP and env vars. Remove `_CONF` or use it for something concrete.

### 6. **Duplicate imports in views**

- **Where:** `music_beta/views.py` lines 10 and 37 (forms imported twice).
- **Change:** Single import for all forms: `CopyrightForm, LoginForm, UserSignupForm, AdCampaignForm, ServiceRequestForm, ClientCampaignForm`.

### 7. **Split large views module**

- **Where:** `music_beta/views.py` (800+ lines, many view functions).
- **Change:** Split by area, e.g. `views/home.py`, `views/auth.py`, `views/client_dashboard.py`, `views/legal.py`, `views/api.py`, and a single `views/__init__.py` or `urls.py` that imports from them. Keeps URLs in one place, views in smaller files.

---

## Lower priority (nice to have)

### 8. **Login/signup with Django auth**

- **Where:** Custom session-based login/signup in `music_beta/views.py`.
- **Issue:** Reinventing login/signup while using AbstractUser; no password reset, no Django auth permissions.
- **Change:** Consider `django.contrib.auth.views.LoginView`/`LogoutView` and a signup view that creates users with `set_password()`, then `login(request, user)`. Use `@login_required` and `request.user` instead of session `user_id` where feasible.

### 9. **REST API consistency**

- **Where:** Some endpoints return JSON (e.g. signup, upload_ad_campaign, search) with manual JSON parsing; others use DRF.
- **Change:** Either standardize JSON APIs on DRF (serializers, viewsets, or APIView) with proper status codes and error format, or document which endpoints are “legacy” JSON and which are DRF.

### 10. **Template/static structure**

- **Where:** `templates/base.html`, `templates/music_beta/*.html`.
- **Change:** Ensure all app templates live under `templates/<app_name>/` and base is the single layout; consider a small template tag or context processor for “current user” from session if you keep session-based auth.

### 11. **Tests and password hashing**

- **Where:** `music_beta/tests.py` (e.g. `self.assertEqual(self.user.password, "password123")`).
- **Issue:** Tests assume plaintext password; they will fail once passwords are hashed.
- **Change:** After switching to `set_password`/`check_password`, create users in tests with `set_password('password123')` and assert with `self.assertTrue(self.user.check_password('password123'))`; do not compare `user.password` to plaintext.

### 12. **Optional: dependency cleanup**

- **Where:** `pyproject.toml` / `uv.lock` (e.g. Wagtail if Django CMS is no longer used).
- **Change:** Remove unused heavy dependencies to speed installs and reduce attack surface; keep only what the current templates and views use.

---

## Summary table

| #  | Area              | Effort | Impact | Suggested order |
|----|-------------------|--------|--------|-----------------|
| 1  | Password hashing  | Medium | High   | 1               |
| 2  | ClientCampaign M2M| Small  | High   | 2               |
| 3  | CSRF              | Medium | High   | 3               |
| 4  | Session user helper | Small | Medium | 4             |
| 5  | Settings email    | Small  | Medium | 5               |
| 6  | Imports           | Small  | Low    | 6               |
| 7  | Split views       | Medium | Medium | 7               |
| 8+ | Auth / API / tests| Larger | Medium | As needed        |

Implementing 1, 2, 4, and 5 gives the best balance of security, correctness, and maintainability with limited change.

---

## Already implemented (this pass)

- **Session user helper:** `music_beta/view_utils.get_session_user(request, require_client=False)` added; `client_dashboard`, `campaign_detail`, `create_campaign`, `edit_campaign`, `add_to_cart`, `remove_from_cart` now use it.
- **ClientCampaign M2M:** `create_campaign` now calls `form.save_m2m()` after saving the campaign so selected tracks are stored.
- **Password hashing:** Signup uses `user.set_password(password)` and login uses `user.check_password(password)`. `generate_fake_data` creates users with `set_password()`.
- **Settings:** Single email block (console in DEBUG, SMTP otherwise via env); removed unused `_CONF`. `DEVELOPER_EMAIL` from env.
- **Imports:** Single form import in `music_beta/views.py`.

**Note:** Existing users created before this change have plaintext passwords; they will not be able to log in until passwords are reset or users are re-created. Unit tests that assert `user.password == "password123"` need to be updated to use `user.check_password("password123")` and to create users with `set_password()`.
