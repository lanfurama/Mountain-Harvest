export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(amount)
}

export function renderStars(rating: number): string {
  return Array(5)
    .fill(0)
    .map((_, i) => {
      if (i < Math.floor(rating)) {
        return '<i class="fas fa-star"></i>'
      } else if (i < rating) {
        return '<i class="fas fa-star-half-alt"></i>'
      } else {
        return '<i class="far fa-star"></i>'
      }
    })
    .join('')
}
