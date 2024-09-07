const moreFilters = document.querySelector('.js-expand-more-filters')
document.querySelector('.js-more-filters')
    .addEventListener('click', () => {
        moreFilters.style.display === 'none' ? moreFilters.style.display = 'block' : moreFilters.style.display ='none'
    })

document.querySelector('.js-more-filter-close')
    .addEventListener('click', () => {
        moreFilters.style.display = 'none'
    })