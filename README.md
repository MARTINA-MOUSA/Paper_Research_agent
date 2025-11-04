Paper2Video
===========

ملخص الفكرة
-----------
- يأخذ ورقة بحثية PDF، يفصلها إلى أقسام مفهومة، يشرحها كفيديو قصير بالعربية.
- يجلب الأوراق الترند من arXiv ويصنفها على مجالات الذكاء الاصطناعي.
- يستخدم Gemini API في: التقسيم، التلخيص، توليد سكربت الفيديو، وتصنيف المجال.

المعمارية (Architecture)
------------------------
- backend/
  - `services/pdf_parser.py`: استخراج نص من PDF.
  - `services/gemini_service.py`: وظائف Gemini
    - `segment_paper(text)` تقسيم الورقة لأقسام بعنوان وملخص مبسط.
    - `summarize_with_gemini(text)` ملخص منظم.
    - `classify_field_with_gemini(text)` تصنيف على مجالات AI.
    - `generate_video_script(sections)` تحويل الأقسام لمشاهد (overlay + narration).
    - `extract_keywords(text)` استخراج كلمات مفتاحية.
  - `services/video_maker.py`: تحويل السكربت إلى فيديو:
    - gTTS لتوليد تعليق صوتي بالعربية.
    - MoviePy لتركيب النص على الشاشة + الصوت.
  - `services/arxiv_service.py`: جلب الأوراق الترند من arXiv RSS.
  - `routers/papers.py`: رفع PDF وإرجاع: summary, field, keywords, sections, script, video_path.
  - `routers/classify.py`: POST نص -> مجال AI باستخدام Gemini.
  - `routers/trends.py`: GET `/trends/trending?category=cs.LG&limit=10` يجلب ترند + تصنيف مجال.
  - `database/` SQLite (SQLAlchemy): جداول `papers`, `trends` (إنشاء تلقائي عند بدء التطبيق).
  - `main.py`: إعداد FastAPI + CORS + تضمين الراوترز + إنشاء الجداول عند التشغيل.

تدفق العمل (Pipeline)
----------------------
1) يرفع المستخدم PDF → `pdf_parser.extract_text_from_pdf`.
2) Gemini يقسم النص → `segment_paper`، ثم يولد سكربت مشاهد → `generate_video_script`.
3) يصنف المجال والكلمات المفتاحية → `classify_field_with_gemini`, `extract_keywords`.
4) `video_maker.make_video_from_scenes` يصنع فيديو MP4 بتعليق صوتي عربي ونصوص على الشاشة.
5) يرجع JSON به كل النتائج + مسار الفيديو.
6) ترند: `trends/trending` يجلب من arXiv ويصنف كل عنصر بمجال AI ويخزن ملخصاً.

التشغيل محلياً
--------------
1) أنشئ ملف بيئة وضع فيه مفتاح Gemini:
```
backend/.env
GEMINI_API_KEY=YOUR_API_KEY
```
2) ثبّت المتطلبات:
```
cd backend
pip install -r requirements.txt
```
3) شغّل السيرفر:
```
uvicorn main:app --reload
```
4) اختبر:
- رفع ورقة: `POST /papers/upload` (multipart file)
- تصنيف نص: `POST /classify/field` body = raw text
- ترند arXiv: `GET /trends/trending?category=cs.LG&limit=10`

ملاحظات
-------
- يعتمد بناء الفيديو على gTTS (صوت عربي) وMoviePy؛ يمكن استبدال الصوت بمحرك TTS آخر عند الحاجة.
- إخراج الفيديو يكتب إلى مجلد `backend/outputs/`.
- يستخدم arXiv RSS عبر `feedparser`؛ يمكن لاحقاً استخدام واجهة بحث أوسع أو فلترة ذكية.

