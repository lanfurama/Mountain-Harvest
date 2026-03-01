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
    def layout(req, title, content, include_editor=False, django_request=None):
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
            head_links.append(Style("""
                /* Quill alignment styles */
                .ql-editor .ql-align-center {
                    text-align: center;
                }
                .ql-editor .ql-align-right {
                    text-align: right;
                }
                .ql-editor .ql-align-justify {
                    text-align: justify;
                }
                /* Center images within aligned blocks */
                .ql-editor .ql-align-center img,
                .ql-editor .ql-align-center .ql-image {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }
                .ql-editor .ql-align-right img,
                .ql-editor .ql-align-right .ql-image {
                    display: block;
                    margin-left: auto;
                    margin-right: 0;
                }
                /* Ensure images are block-level for proper alignment */
                .ql-editor img {
                    max-width: 100%;
                    height: auto;
                }
                /* Image resize handles */
                .ql-editor img {
                    cursor: pointer;
                }
            """))
            scripts.append(Script(src="https://cdn.quilljs.com/1.3.6/quill.min.js"))
            scripts.append(Script(src="https://cdn.jsdelivr.net/npm/quill-image-resize-module@3.0.0/image-resize.min.js"))
            scripts.append(Script("""
                document.addEventListener('DOMContentLoaded', function() {
                    if (typeof Quill !== 'undefined') {
                        var editorEl = document.getElementById('news-content-editor');
                        var contentInput = document.getElementById('news-content');
                        if (!editorEl) return;
                        
                        // Create image modal HTML
                        var imageModalHtml = `
                            <div id="quill-image-modal" class="fixed inset-0 z-50 hidden items-center justify-center bg-black bg-opacity-50">
                                <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
                                    <div class="flex justify-between items-center mb-4">
                                        <h3 class="text-lg font-semibold text-gray-900">Chèn ảnh</h3>
                                        <button id="quill-image-modal-close" class="text-gray-400 hover:text-gray-600">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                    <div class="mb-4">
                                        <label class="block text-sm font-medium text-gray-700 mb-2">URL ảnh:</label>
                                        <input type="text" id="quill-image-url" 
                                               class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#2F5233] focus:border-transparent"
                                               placeholder="https://example.com/image.jpg">
                                    </div>
                                    <div id="quill-image-preview" class="mb-4 hidden">
                                        <label class="block text-sm font-medium text-gray-700 mb-2">Preview:</label>
                                        <img id="quill-image-preview-img" src="" alt="Preview" 
                                             class="max-w-full h-auto rounded border border-gray-300">
                                    </div>
                                    <div class="flex justify-end gap-2">
                                        <button id="quill-image-cancel" 
                                                class="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition">
                                            Hủy
                                        </button>
                                        <button id="quill-image-insert" 
                                                class="px-4 py-2 text-white bg-[#2F5233] rounded-md hover:bg-[#1a331d] transition">
                                            Chèn ảnh
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                        document.body.insertAdjacentHTML('beforeend', imageModalHtml);
                        
                        var imageModal = document.getElementById('quill-image-modal');
                        var imageUrlInput = document.getElementById('quill-image-url');
                        var imagePreview = document.getElementById('quill-image-preview');
                        var imagePreviewImg = document.getElementById('quill-image-preview-img');
                        var imageInsertBtn = document.getElementById('quill-image-insert');
                        var imageCancelBtn = document.getElementById('quill-image-cancel');
                        var imageModalClose = document.getElementById('quill-image-modal-close');
                        
                        function closeImageModal() {
                            imageModal.classList.add('hidden');
                            imageModal.classList.remove('flex');
                            imageUrlInput.value = '';
                            imagePreview.classList.add('hidden');
                        }
                        
                        function showImageModal() {
                            imageModal.classList.remove('hidden');
                            imageModal.classList.add('flex');
                            imageUrlInput.focus();
                        }
                        
                        function updateImagePreview() {
                            var url = imageUrlInput.value.trim();
                            if (url && (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:image/') || url.startsWith('/'))) {
                                imagePreviewImg.src = url;
                                imagePreview.classList.remove('hidden');
                                imagePreviewImg.onerror = function() {
                                    imagePreview.classList.add('hidden');
                                };
                            } else {
                                imagePreview.classList.add('hidden');
                            }
                        }
                        
                        imageUrlInput.addEventListener('input', updateImagePreview);
                        imageUrlInput.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                imageInsertBtn.click();
                            }
                        });
                        
                        imageModalClose.addEventListener('click', closeImageModal);
                        imageCancelBtn.addEventListener('click', closeImageModal);
                        imageModal.addEventListener('click', function(e) {
                            if (e.target === imageModal) {
                                closeImageModal();
                            }
                        });
                        
                        // Function to initialize Quill with image resize if available
                        function initQuill() {
                            var quillConfig = {
                                theme: 'snow',
                                modules: {
                                    toolbar: {
                                        container: [
                                            [{ 'header': [false, 1, 2, 3, false] }],
                                            ['bold', 'italic', 'underline', 'strike'],
                                            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                                            [{ 'indent': '-1'}, { 'indent': '+1' }],
                                            [{ 'align': [] }],
                                            ['link', 'image'],
                                            ['clean']
                                        ],
                                        handlers: {
                                            'image': function() {
                                                showImageModal();
                                                imageInsertBtn.onclick = function() {
                                                    var url = imageUrlInput.value.trim();
                                                    if (url) {
                                                        var range = quill.getSelection(true);
                                                        if (!range) {
                                                            range = { index: quill.getLength(), length: 0 };
                                                        }
                                                        quill.insertEmbed(range.index, 'image', url, 'user');
                                                        closeImageModal();
                                                    }
                                                };
                                            }
                                        }
                                    }
                                },
                                placeholder: 'Nhập nội dung bài viết...',
                                formats: ['header', 'bold', 'italic', 'underline', 'strike', 
                                         'list', 'bullet', 'indent', 'align', 'link', 'image']
                            };
                            
                            // Try to add image resize module if available
                            // When loaded via CDN script tag, the module auto-registers
                            // Just check if it's available and add to config
                            var hasImageResize = false;
                            try {
                                // Check various ways the module might be exposed
                                if (typeof ImageResize !== 'undefined' || 
                                    typeof window.ImageResize !== 'undefined' ||
                                    typeof QuillImageResize !== 'undefined') {
                                    hasImageResize = true;
                                }
                            } catch (e) {
                                // Ignore
                            }
                            
                            if (hasImageResize) {
                                // Use lowercase 'imageResize' as module name
                                quillConfig.modules.imageResize = {};
                            }
                            
                            return new Quill('#news-content-editor', quillConfig);
                        }
                        
                        // Function to setup Quill after initialization
                        var quill;
                        var quillInitialized = false;
                        
                        function setupQuill(quillInstance) {
                            quill = quillInstance;
                            quillInitialized = true;
                            window.newsQuillEditor = quill;
                            
                            if (!contentInput) return;
                            
                            var initialContent = contentInput.value || '';
                            if (initialContent) {
                                try {
                                    quill.root.innerHTML = initialContent;
                                } catch (e) {
                                    console.warn('Could not parse initial content:', e);
                                    quill.setText(initialContent);
                                }
                            }
                            contentInput.value = quill.root.innerHTML;
                            
                            // Fix auto-scroll issue when formatting
                            var editorContainer = quill.container;
                            var quillEditor = quill.root;
                            var savedScrollTop = 0;
                            var savedSelection = null;
                            var isFormatting = false;
                            var restoreTimeout = null;
                            
                            // Save current scroll position and selection
                            function saveEditorState() {
                                savedScrollTop = editorContainer.scrollTop || quillEditor.scrollTop || 0;
                                var selection = quill.getSelection();
                                if (selection) {
                                    savedSelection = { index: selection.index, length: selection.length };
                                }
                            }
                            
                            // Restore scroll position using requestAnimationFrame for smooth restore
                            function restoreScrollPosition() {
                                if (restoreTimeout) {
                                    cancelAnimationFrame(restoreTimeout);
                                }
                                
                                function restore() {
                                    if (editorContainer) {
                                        editorContainer.scrollTop = savedScrollTop;
                                    }
                                    if (quillEditor) {
                                        quillEditor.scrollTop = savedScrollTop;
                                    }
                                }
                                
                                // Restore immediately and also after a few frames
                                restore();
                                requestAnimationFrame(function() {
                                    restore();
                                    requestAnimationFrame(function() {
                                        restore();
                                    });
                                });
                            }
                            
                            // Prevent scroll on toolbar interactions
                            var toolbar = quill.getModule('toolbar');
                            if (toolbar && toolbar.container) {
                                // Capture state before any toolbar interaction
                                toolbar.container.addEventListener('mousedown', function(e) {
                                    saveEditorState();
                                    isFormatting = true;
                                }, true);
                                
                                toolbar.container.addEventListener('click', function(e) {
                                    saveEditorState();
                                    isFormatting = true;
                                }, true);
                                
                                toolbar.container.addEventListener('mouseup', function(e) {
                                    saveEditorState();
                                }, true);
                            }
                            
                            // Monitor selection changes but don't save during formatting
                            quill.on('selection-change', function(range) {
                                if (!isFormatting && range) {
                                    saveEditorState();
                                }
                            });
                            
                            // Restore scroll after format operations
                            quill.on('text-change', function(delta, oldDelta, source) {
                                contentInput.value = quill.root.innerHTML;
                                
                                if (isFormatting && source === 'user') {
                                    // Use multiple restore attempts
                                    restoreScrollPosition();
                                    
                                    // Also restore selection if we had one
                                    if (savedSelection) {
                                        setTimeout(function() {
                                            try {
                                                quill.setSelection(savedSelection.index, savedSelection.length, 'silent');
                                            } catch (e) {
                                                // Selection might be invalid, ignore
                                            }
                                        }, 0);
                                    }
                                    
                                    // Reset formatting flag after a delay
                                    setTimeout(function() {
                                        isFormatting = false;
                                    }, 100);
                                }
                            });
                            
                            // Use MutationObserver to catch DOM changes and restore scroll
                            if (window.MutationObserver) {
                                var observer = new MutationObserver(function(mutations) {
                                    if (isFormatting) {
                                        restoreScrollPosition();
                                    }
                                });
                                
                                observer.observe(quillEditor, {
                                    childList: true,
                                    subtree: true,
                                    attributes: true,
                                    attributeFilter: ['class', 'style']
                                });
                            }
                            
                            // Prevent scroll on focus (but allow user scrolling)
                            var userScrolling = false;
                            quillEditor.addEventListener('scroll', function() {
                                if (!userScrolling && isFormatting) {
                                    restoreScrollPosition();
                                }
                            });
                            
                            // Track user-initiated scrolling
                            quillEditor.addEventListener('wheel', function() {
                                userScrolling = true;
                                setTimeout(function() {
                                    userScrolling = false;
                                }, 500);
                            });
                            
                            quillEditor.addEventListener('touchmove', function() {
                                userScrolling = true;
                                setTimeout(function() {
                                    userScrolling = false;
                                }, 500);
                            });
                            
                            var form = contentInput.closest('form');
                            if (form) {
                                form.addEventListener('submit', function(e) {
                                    contentInput.value = quill.root.innerHTML;
                                });
                            }
                        }
                        
                        // Initialize Quill
                        // ImageResize module from CDN loads asynchronously, so we wait a bit
                        function tryInitQuill() {
                            // Check if ImageResize is available (from CDN)
                            if (typeof ImageResize !== 'undefined' || typeof window.ImageResize !== 'undefined') {
                                setupQuill(initQuill());
                                return true;
                            }
                            return false;
                        }
                        
                        // Try immediately
                        if (!tryInitQuill()) {
                            // Wait for script to load (max 2 seconds)
                            var checkImageResize = setInterval(function() {
                                if (tryInitQuill()) {
                                    clearInterval(checkImageResize);
                                }
                            }, 100);
                            
                            // Fallback: init without resize after 2 seconds
                            setTimeout(function() {
                                if (!quillInitialized) {
                                    clearInterval(checkImageResize);
                                    setupQuill(initQuill());
                                }
                            }, 2000);
                        }
                    }
                });
            """))
        # Add inline script to define confirmDelete immediately
        scripts.append(Script("""
            // Define confirmDelete immediately to avoid timing issues
            window.confirmDelete = function(id, url) {
                if (!id || id === 'None' || !url || url.includes('None')) {
                    console.error('Invalid delete parameters:', id, url);
                    return;
                }
                
                // Get CSRF token from cookie or meta tag
                function getCookie(name) {
                    var cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        var cookies = document.cookie.split(';');
                        for (var i = 0; i < cookies.length; i++) {
                            var cookie = cookies[i].trim();
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                }
                
                function getCSRFToken() {
                    var metaTag = document.querySelector('meta[name="csrf-token"]');
                    if (metaTag) {
                        return metaTag.getAttribute('content');
                    }
                    return getCookie('csrftoken');
                }
                
                var deleteAction = {
                    url: url,
                    csrfToken: getCSRFToken()
                };
                
                if (typeof openConfirm === 'function') {
                    openConfirm('Bạn có chắc chắn muốn xóa mục này không?', deleteAction);
                } else {
                    // Fallback if admin.js not loaded yet
                    if (confirm('Bạn có chắc chắn muốn xóa mục này không?')) {
                        var form = document.createElement('form');
                        form.method = 'POST';
                        form.action = url;
                        form.style.display = 'none';
                        
                        if (deleteAction.csrfToken) {
                            var csrfInput = document.createElement('input');
                            csrfInput.type = 'hidden';
                            csrfInput.name = 'csrfmiddlewaretoken';
                            csrfInput.value = deleteAction.csrfToken;
                            form.appendChild(csrfInput);
                        }
                        
                        document.body.appendChild(form);
                        form.submit();
                    }
                }
            };
        """))
        scripts.append(Script(src="/js/admin.js"))
        # Add responsive meta and viewport
        meta_charset = Meta(charset="UTF-8")
        meta_viewport = Meta(name="viewport", content="width=device-width, initial-scale=1.0")
        
        # Add CSRF token meta tag if request is available
        csrf_meta = None
        try:
            from django.middleware.csrf import get_token
            # Try to get CSRF token from django_request if available
            if django_request:
                csrf_token = get_token(django_request)
                if csrf_token:
                    csrf_meta = Meta(name="csrf-token", content=csrf_token)
        except:
            pass
        
        head_elements = [meta_charset, meta_viewport, Title(f"{title} - Admin")]
        if csrf_meta:
            head_elements.append(csrf_meta)
        head_elements.extend(head_links)
        
        return Html(
            Head(
                *head_elements,
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
