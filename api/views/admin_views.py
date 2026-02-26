"""Admin views for HTML rendering."""
from fasthtml.common import *


class AdminViews:
    """Views for Admin HTML rendering."""
    
    NAV_ITEMS = [
        ("/admin", "fa-gauge-high", "Dashboard"),
        ("/admin/categories", "fa-folder", "Categories"),
        ("/admin/products", "fa-box", "Products"),
        ("/admin/news", "fa-newspaper", "News"),
        ("/admin/pages", "fa-file-alt", "Pages"),
        ("/admin/hero", "fa-image", "Hero"),
        ("/admin/site", "fa-cog", "Site Config"),
    ]
    
    @staticmethod
    def layout(req, title, content, include_editor=False):
        """Render admin layout."""
        path = req.url.path
        
        def nav_link(href, icon, label):
            active = (path == href) or (href != "/admin" and path.startswith(href))
            cls = "flex items-center gap-2 px-3 py-2 rounded text-white/80 hover:bg-white/10 hover:text-white transition"
            if active:
                cls = "flex items-center gap-2 px-3 py-2 rounded bg-[#1a331d] text-white"
            return A(I(cls=f"fas {icon} w-5"), Span(label), href=href, cls=cls)
        
        sidebar = Aside(id="admin-sidebar", cls="w-64 fixed inset-y-0 left-0 z-30 bg-[#2F5233] text-white flex flex-col transform transition-transform duration-300 ease-in-out lg:translate-x-0 -translate-x-full")(
            Div(cls="p-3 border-b border-white/10")(
                A(cls="flex items-center gap-2 text-white hover:text-white/80", href="/admin")(
                    I(cls="fas fa-mountain text-2xl"),
                    Span("Mountain Harvest", cls="font-bold text-lg"),
                ),
            ),
            Nav(cls="flex-1 p-3 space-y-0.5")(
                *[nav_link(href, icon, label) for href, icon, label in AdminViews.NAV_ITEMS],
            ),
            Div(cls="p-3 border-t border-white/10")(
                A(cls="flex items-center gap-2 px-3 py-2 rounded text-white/80 hover:bg-white/10 hover:text-white transition", href="/")(
                    I(cls="fas fa-external-link-alt w-5"),
                    Span("Về trang chủ"),
                ),
            ),
        )
        overlay = Div(id="admin-sidebar-overlay", cls="fixed inset-0 bg-black/50 z-20 lg:hidden hidden")
        header_bar = Div(cls="lg:hidden flex items-center justify-between p-3 bg-white border-b shadow-sm")(
            Button(id="admin-sidebar-toggle", type="button", cls="p-1.5 rounded text-[#2F5233] hover:bg-[#2F5233]/10", title="Menu")(
                I(cls="fas fa-bars text-xl"),
            ),
            Span(title, cls="font-semibold text-gray-800"),
            Span(cls="w-10"),
        )
        main = Main(cls="lg:ml-64 ml-0 flex-1 min-h-screen")(
            header_bar,
            Div(cls="p-2 lg:p-3 bg-[#F1F0E8] min-h-screen")(
                Div(cls="bg-white rounded shadow-sm border border-[#2F5233]/10 p-3")(content),
            ),
        )
        toast_el = Div(id="admin-toast", cls="fixed bottom-4 right-4 z-50 hidden transform transition-all duration-300 translate-y-4 opacity-0")
        confirm_modal = Div(id="admin-confirm-modal", cls="fixed inset-0 z-50 hidden flex items-center justify-center p-3")(
            Div(id="admin-confirm-overlay", cls="absolute inset-0 bg-black/50"),
            Div(id="admin-confirm-dialog", cls="relative bg-white rounded shadow-xl max-w-md w-full p-3")(
                P(id="admin-confirm-message", cls="text-gray-700 mb-4"),
                Div(cls="flex gap-2 justify-end")(
                    Button(id="admin-confirm-cancel", type="button", cls="px-3 py-1.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-50 text-sm"),
                    Button(id="admin-confirm-ok", type="button", cls="px-3 py-1.5 rounded bg-[#2F5233] text-white hover:bg-[#1a331d] text-sm"),
                ),
            ),
        )
        tailwind_config = Script("""
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            brand: {
                                green: '#2F5233',
                                darkGreen: '#1a331d',
                                light: '#76885B',
                                brown: '#8B5A2B',
                                cream: '#F1F0E8',
                                orange: '#E85D04'
                            }
                        }
                    }
                }
            };
        """)
        scripts = [Script(src="https://cdn.tailwindcss.com"), tailwind_config]
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
        scripts.append(Script(src="/js/admin.js"))
        return Html(
            Head(
                Title(f"{title} - Admin"),
                *head_links,
            ),
            Body(
                *scripts,
                Div(cls="flex min-h-screen relative")(
                    overlay,
                    sidebar,
                    main,
                    toast_el,
                    confirm_modal,
                ),
            ),
        )
