console.log("Clicked");
const moreFilters = document.querySelector('.js-expand-more-filters')
document.querySelector('.js-more-filters')
    .addEventListener('click', () => {
        moreFilters.style.display === 'none' ? moreFilters.style.display = 'block' : moreFilters.style.display ='none'

    })


document.querySelector('.js-more-filter-close')
    .addEventListener('click', () => {
        moreFilters.style.display = 'none'
    })

document.querySelectorAll('.job-card')
    .forEach((jobCard) => {
        jobCard.addEventListener('click', () => {
            window.location.href = 'apply.html'
        })
    })
    
export const fetchJobData = () => {
    fetch(
        'http://127.0.0.1:8000/jobs'
        ).then((response) => {
            return response.json() 
    
        }).then((Jobs) => {
            // console.log(Jobs)
        })
        .catch((error) => {
        console.log('Unexpected error. Please try again later');
      })

} 


    