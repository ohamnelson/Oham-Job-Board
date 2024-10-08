// import { fetchJobData } from "./jobs";
let currentOffset = 0;
const limit = 10;
let jobs = []
let title = document.querySelector('.job-search-bar').value
let location = document.querySelector('.job-search-bar').value
const getSelectedRadioValue = () => {
    let selectedRadio = document.querySelector('input[name="datePosted"]:checked');
    return selectedRadio ? selectedRadio.value : '';  // Return value if selected, otherwise return null
};
let date = getSelectedRadioValue();
    


const fetchJobData = async (limit, offset, title= '', location='', date='') => {
    let url = `http://127.0.0.1:8000/jobs?offset=${offset}&limit=${limit}`;
    if(title) {
        url +=`&title=${title}`
    }
    if(location) {
        url += `&location=${location}`
    }
    if(date) {
        url += `&date=${date}`
    }
    const response = await fetch(url);
    const data =  await response.json() 
    return data
    
}

// Function to display job cards
const displayJobs = async (jobsData, jobsFound=0) => {
    
    let jobsHTML = '';

    // Store the fetched jobs in the globally accessible jobs array
    jobs.push(...jobsData); // Append new jobs to the jobs array

    jobsData.forEach((job) => { // Iterate through the jobs and create HTML for each
        jobsHTML += `
            <div class="job-card">
                <img class="job-card-logo" src="${job.CompanyLogo}"height="80px" width="80px">
                <div class="job-card-text">
                    <p class="job-card-title">${job.Title}</p>
                    <p class="job-card-company">${job.CompanyName}</p>
                    <p class="job-card-location">${job.Location}</p>
                    <p class="job-card-date">${job.PublicationDate}</p>
                </div>
            </div>`;
    });
    document.querySelector('.js-jobs-found').innerHTML = `${jobsFound} jobs found`;
    document.querySelector('.js-job-card-section').innerHTML += jobsHTML; // Insert the job cards into the DOM
};
// displayJobs();

// Function to load more jobs when user scrolls near the bottom
const loadMoreJobs = async (title="", location="", date="") => {
    let jobsData = await fetchJobData(limit, currentOffset, title, location, date); // Fetch jobs with pagination
    displayJobs(jobsData['jobs'], jobsData['jobCount']);  // Render the jobs
    currentOffset += limit;  // Increment the offset
};


document.querySelector('.job-search-button')
    .addEventListener('click', async () => {
        title = document.querySelector('.job-search-bar').value;
        location = document.querySelector('.job-location-filter').value;
        date = getSelectedRadioValue();
        console.log(date)
        jobs = []
        currentOffset = 0
        const jobsData = await fetchJobData(limit, currentOffset, title, location, date); // Fetch jobs with pagination
        document.querySelector('.js-job-card-section').innerHTML = ''
        displayJobs(jobsData['jobs'], jobsData['jobCount'])
        currentOffset += limit;
        document.querySelector('.js-expand-more-filters').style.display = 'none'
    })


// Initial Load
loadMoreJobs();

// Infinite scroll event listener
window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        // If the user is near the bottom, load more jobs
        // console.log(title)
        loadMoreJobs(title, location, date);
    }
});





const moreFilters = document.querySelector('.js-expand-more-filters')
document.querySelector('.js-more-filters')
    .addEventListener('click', () => {
        moreFilters.style.display === 'none' ? moreFilters.style.display = 'block' : moreFilters.style.display ='none'
    })

document.querySelector('.js-more-filter-close')
    .addEventListener('click', () => {
        moreFilters.style.display = 'none'
    })


// Event listeners for job card click
document.addEventListener('click', (e) => {
    if (e.target.closest('.job-card')) {
        const jobCard = e.target.closest('.job-card');
        const jobIndex = Array.from(document.querySelectorAll('.job-card')).indexOf(jobCard);
        window.location.href = `apply.html?jobId=${jobs[jobIndex].Id}`;
    }
});