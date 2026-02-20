"""Admin views for HTML rendering."""
from fasthtml.common import *


class AdminViews:
    """Views for Admin HTML rendering."""
    
    NAV_ITEMS = [
        ("/admin", "fa-gauge-high", "Dashboard"),
        ("/admin/products", "fa-box", "Products"),
        ("/admin/news", "fa-newspaper", "News"),
        ("/admin/hero", "fa-image", "Hero"),
        ("/admin/site", "fa-cog", "Site Config"),
    ]
    
    @staticmethod
    def layout(req, title, content, include_editor=False):
        """Render admin layout."""
        path = req.url.path
        
        def nav_link(href, icon, label):
            active = (path == href) or (href != "/admin" and path.startswith(href))
            cls = "flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition"
            if active:
                cls = "flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-700 text-white"
            return A(I(cls=f"fas {icon} w-5"), Span(label), href=href, cls=cls)
        
        sidebar = Aside(cls="w-64 fixed inset-y-0 left-0 bg-gray-800 text-white flex flex-col")(
            Div(cls="p-6 border-b border-gray-700")(
                A(cls="flex items-center gap-2 text-white hover:text-gray-300", href="/admin")(
                    I(cls="fas fa-mountain text-2xl"),
                    Span("Mountain Harvest", cls="font-bold text-lg"),
                ),
            ),
            Nav(cls="flex-1 p-4 space-y-1")(
                *[nav_link(href, icon, label) for href, icon, label in AdminViews.NAV_ITEMS],
            ),
            Div(cls="p-4 border-t border-gray-700")(
                A(cls="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-300 hover:bg-gray-700 hover:text-white transition", href="/")(
                    I(cls="fas fa-external-link-alt w-5"),
                    Span("Về trang chủ"),
                ),
            ),
        )
        main = Main(cls="ml-64 flex-1 p-6 bg-gray-50 min-h-screen")(
            Div(cls="bg-white rounded-lg shadow p-6")(content),
        )
        scripts = [Script(src="https://cdn.tailwindcss.com")]
        head_links = [Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css")]
        if include_editor:
            head_links.append(Link(rel="stylesheet", href="https://cdn.quilljs.com/1.3.6/quill.snow.css"))
            scripts.append(Script(src="https://cdn.quilljs.com/1.3.6/quill.min.js"))
            scripts.append(Script("""
                document.addEventListener('DOMContentLoaded', function() {
                    if (typeof Quill !== 'undefined') {
                        var editorEl = document.getElementById('news-content-editor');
                        var contentInput = document.getElementById('news-content');
                        if (!editorEl) return;
                        
                        var quill = new Quill('#news-content-editor', {
                            theme: 'snow',
                            modules: {
                                toolbar: [
                                    [{ 'header': [1, 2, 3, false] }],
                                    ['bold', 'italic', 'underline', 'strike'],
                                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                                    [{ 'align': [] }],
                                    ['link', 'image'],
                                    ['clean']
                                ]
                            },
                            placeholder: 'Nhập nội dung...'
                        });
                        
                        if (contentInput && quill) {
                            var initialContent = contentInput.value || editorEl.innerHTML || '';
                            quill.root.innerHTML = initialContent;
                            contentInput.value = initialContent;
                            
                            quill.on('text-change', function() {
                                contentInput.value = quill.root.innerHTML;
                            });
                            
                            var form = contentInput.closest('form');
                            if (form) {
                                form.addEventListener('submit', function() {
                                    contentInput.value = quill.root.innerHTML;
                                });
                            }
                        }
                    }
                });
            """))
        return Html(
            Head(
                Title(f"{title} - Admin"),
                *head_links,
            ),
            Body(
                *scripts,
                Div(cls="flex min-h-screen")(sidebar, main),
            ),
        )
