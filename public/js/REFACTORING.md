# JavaScript Refactoring Documentation

## Overview
Codebase đã được refactor để tối ưu và dễ bảo trì hơn với cấu trúc module rõ ràng.

## Cấu trúc Modules

### 1. `config.js` - Configuration & Constants
- Tất cả constants và configuration tập trung
- Dễ dàng thay đổi mà không cần sửa nhiều file
- Bao gồm: pagination, API settings, UI constants, selectors

### 2. `utils.js` - Utility Functions
- Common functions được tái sử dụng
- Bao gồm:
  - `escapeHtml()` - XSS protection
  - `formatCurrency()` - Currency formatting
  - `$()` / `$$()` - DOM query helpers
  - `debounce()` / `throttle()` - Performance optimization
  - `getUrlParams()` / `buildUrl()` - URL manipulation
  - `scrollTo()` - Smooth scrolling
  - `getStorage()` / `setStorage()` - Safe localStorage

### 3. `api.js` - API Client
- Centralized API calls với error handling
- Retry logic tự động
- Timeout handling
- Methods: `get()`, `post()`, `put()`, `delete()`
- Namespaced endpoints: `ApiClient.news.list()`, `ApiClient.products.get()`

## Cải thiện chính

### 1. Code Reusability
- Loại bỏ duplicate code (escapeHtml, fetch patterns)
- Utilities có thể tái sử dụng ở mọi nơi

### 2. Error Handling
- Consistent error handling qua ApiClient
- Retry logic tự động
- Better error messages

### 3. Performance
- Throttle/debounce cho scroll events
- Optimized DOM queries
- Lazy loading support

### 4. Maintainability
- Clear separation of concerns
- Easy to test
- Easy to extend

## Migration Guide

### Before:
```javascript
const res = await fetch('/api/news');
const data = await res.json();
```

### After:
```javascript
const response = await ApiClient.news.list();
if (response.ok) {
  const data = response.data;
}
```

### Before:
```javascript
document.getElementById('element-id')
```

### After:
```javascript
Utils.$('element-id')
```

### Before:
```javascript
amount.toLocaleString('vi-VN') + 'đ'
```

### After:
```javascript
Utils.formatCurrency(amount)
```

## Best Practices

1. **Luôn sử dụng Utils functions** thay vì native methods khi có thể
2. **Sử dụng ApiClient** cho tất cả API calls
3. **Tham chiếu Config** cho constants thay vì hardcode
4. **Error handling** luôn check `response.ok` trước khi dùng data
5. **Performance** sử dụng throttle/debounce cho events

## Next Steps

- [ ] Refactor `news.js` để sử dụng ApiClient
- [ ] Refactor `products.js` để sử dụng ApiClient và Utils
- [ ] Refactor `cart.js` để sử dụng Utils storage helpers
- [ ] Add unit tests cho utilities
- [ ] Add JSDoc comments cho tất cả functions
