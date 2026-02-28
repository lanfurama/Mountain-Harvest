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
            base_cls = "flex items-center gap-2 px-3 py-2 rounded text-white/90 hover:bg-white/10 hover:text-white transition-all duration-200 group"
            if active:
                base_cls = "flex items-center gap-2 px-3 py-2 rounded bg-white/15 text-white shadow-sm border-l-2 border-white/30"
            return A(
                I(cls=f"fas {icon} w-5 text-center"),
                Span(label, cls="font-medium"),
                href=href, 
                cls=base_cls
            )
        
        sidebar = Aside(
            id="admin-sidebar",
            cls="w-64 fixed inset-y-0 left-0 z-30 bg-gradient-to-b from-[#2F5233] via-[#2a4a2e] to-[#1a331d] text-white flex flex-col shadow-2xl transform transition-transform duration-300 ease-in-out lg:translate-x-0 -translate-x-full"
        )(
            Div(cls="p-3 border-b border-white/10 bg-white/5")(
                A(cls="flex items-center gap-2 text-white hover:text-white/90 transition", href="/admin")(
                    Div(cls="w-8 h-8 rounded bg-white/15 flex items-center justify-center")(
                        I(cls="fas fa-mountain text-lg"),
                    ),
                    Div(
                        Span("Mountain Harvest", cls="font-bold text-base block"),
                        Span("Admin Panel", cls="text-xs text-white/70 block"),
                    ),
                ),
            ),
            Nav(cls="flex-1 p-3 space-y-1 overflow-y-auto")(
                *[nav_link(href, icon, label) for href, icon, label in AdminViews.NAV_ITEMS],
            ),
            Div(cls="p-3 border-t border-white/10 bg-white/5")(
                A(
                    cls="flex items-center gap-2 px-3 py-2 rounded text-white/90 hover:bg-white/10 hover:text-white transition-all duration-200",
                    href="/"
                )(
                    I(cls="fas fa-external-link-alt w-5"),
                    Span("Về trang chủ", cls="font-medium"),
                ),
                Div(cls="mt-2 pt-2 border-t border-white/10")(
                    Div(cls="flex items-center gap-2 px-2 py-1.5")(
                        Div(cls="w-7 h-7 rounded bg-white/15 flex items-center justify-center")(
                            I(cls="fas fa-user-circle text-sm"),
                        ),
                        Div(cls="flex-1 min-w-0")(
                            Span("Admin User", cls="text-sm font-medium block truncate"),
                            Span("admin@mountainharvest.com", cls="text-xs text-white/70 block truncate"),
                        ),
                    ),
                ),
            ),
        )
        overlay = Div(id="admin-sidebar-overlay", cls="fixed inset-0 bg-black/60 backdrop-blur-sm z-20 lg:hidden hidden transition-opacity duration-300")
        header_bar = Div(cls="lg:hidden flex items-center justify-between p-3 bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10")(
            Button(
                id="admin-sidebar-toggle",
                type="button",
                cls="p-1.5 rounded text-[#2F5233] hover:bg-gray-100 active:bg-gray-200 transition",
                title="Menu"
            )(
                I(cls="fas fa-bars text-lg"),
            ),
            Span(title, cls="font-semibold text-gray-900 text-base"),
            Span(cls="w-8"),
        )
        desktop_header = Div(cls="hidden lg:flex items-center justify-between p-4 bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10")(
            Div(
                H1(title, cls="text-xl font-bold text-gray-900"),
                Span("Quản lý nội dung và cấu hình", cls="text-sm text-gray-500 mt-0.5 block"),
            ),
            Div(cls="flex items-center gap-2")(
                Button(
                    type="button",
                    cls="p-1.5 rounded text-gray-600 hover:bg-gray-100 transition",
                    title="Thông báo"
                )(
                    I(cls="fas fa-bell text-base"),
                ),
                Button(
                    type="button",
                    cls="p-1.5 rounded text-gray-600 hover:bg-gray-100 transition",
                    title="Cài đặt"
                )(
                    I(cls="fas fa-cog text-base"),
                ),
                Div(cls="w-7 h-7 rounded bg-gradient-to-br from-[#2F5233] to-[#1a331d] flex items-center justify-center cursor-pointer")(
                    I(cls="fas fa-user text-white text-xs"),
                ),
            ),
        )
        main = Main(cls="lg:ml-64 ml-0 flex-1 min-h-screen bg-gradient-to-br from-gray-50 to-[#F1F0E8]")(
            header_bar,
            desktop_header,
            Div(cls="p-3 lg:p-4 min-h-screen")(
                Div(cls="max-w-7xl mx-auto")(
                    Div(cls="bg-white rounded shadow-sm border border-gray-200 p-4 lg:p-5")(content),
                ),
            ),
        )
        toast_el = Div(id="admin-toast", cls="fixed bottom-4 right-4 z-50 hidden transform transition-all duration-300 translate-y-4 opacity-0")
        toast_progress = Div(id="admin-toast-progress", cls="absolute bottom-0 left-0 h-1 bg-white/30 rounded-b transition-all duration-300")
        confirm_modal = Div(id="admin-confirm-modal", cls="fixed inset-0 z-50 hidden flex items-center justify-center p-3 backdrop-blur-sm")(
            Div(id="admin-confirm-overlay", cls="absolute inset-0 bg-black/60 transition-opacity"),
            Div(id="admin-confirm-dialog", cls="relative bg-white rounded shadow-xl max-w-md w-full transform transition-all duration-300 scale-95 opacity-0 p-4")(
                Div(cls="flex items-center gap-3 mb-3")(
                    Div(cls="w-10 h-10 rounded bg-red-100 flex items-center justify-center")(
                        I(cls="fas fa-exclamation-triangle text-red-600 text-lg"),
                    ),
                    H3("Xác nhận", cls="text-lg font-bold text-gray-900"),
                ),
                P(id="admin-confirm-message", cls="text-gray-700 mb-4 pl-13"),
                Div(cls="flex gap-2 justify-end")(
                    Button(id="admin-confirm-cancel", type="button", cls="px-3 py-1.5 rounded border border-gray-300 text-gray-700 hover:bg-gray-50 font-medium transition"),
                    Button(id="admin-confirm-ok", type="button", cls="px-3 py-1.5 rounded bg-red-600 text-white hover:bg-red-700 font-medium shadow-sm transition"),
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
        # Add responsive meta and viewport
        meta_viewport = Meta(name="viewport", content="width=device-width, initial-scale=1.0")
        return Html(
            Head(
                meta_viewport,
                Title(f"{title} - Admin"),
                *head_links,
                Style("""
                    @media (max-width: 768px) {
                        /* Touch-friendly buttons on mobile */
                        button, a[role="button"], .btn {
                            min-height: 44px;
                            min-width: 44px;
                        }
                        /* Better form spacing on mobile */
                        form .grid {
                            grid-template-columns: 1fr !important;
                        }
                    }
                    /* Smooth scroll */
                    html {
                        scroll-behavior: smooth;
                    }
                    /* Better select appearance */
                    select {
                        background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
                        background-position: right 0.5rem center;
                        background-repeat: no-repeat;
                        background-size: 1.5em 1.5em;
                        padding-right: 2.5rem;
                    }
                """),
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
