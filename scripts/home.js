// import { fetchSimilarJob } from "./apply.js";
const limit = 10;
let currentOffset = 0;
let offset = 0;
let jobs = []
let title = document.querySelector('.job-search-bar').value
let location = document.querySelector('.job-search-bar').value
let dropdown = document.getElementById('sort-selection')
let sortValue = dropdown.value
let similarJobsList = []

// console.log(currentOffset)

const getSelectedRadioValue = () => {
    let selectedRadio = document.querySelector('input[name="datePosted"]:checked');
    return selectedRadio ? selectedRadio.value : '';  // Return value if selected, otherwise return null
};

let date = getSelectedRadioValue();

    
const fetchJobData = async (title= '', location='', date='', sortValue='') => {
    let url = `http://127.0.0.1:8000/jobs?offset=${currentOffset}&limit=${limit}`;
    if(title) {
        url +=`&title=${title}`
    }
    if(location) {
        url += `&location=${location}`
    }
    if(date) {
        url += `&date=${date}`
    }
    if(sortValue) {
        url += `&sort=${sortValue}`
    }
    // console.log(url)
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

// Function to load more jobs when user scrolls near the bottom
const loadMoreJobs = async (title="", location="", date="", sortValue="") => {
    let jobsData = await fetchJobData(title, location, date, sortValue); // Fetch jobs with pagination
    console.log(jobsData)
    displayJobs(jobsData['jobs'], jobsData['jobCount']);  // Render the jobs
    currentOffset += limit;  // Increment the offset
    // console.log(currentOffset)
};


document.querySelectorAll('.js-job-search-button, .js-big-job-search-button')
    .forEach(button => {
        button.addEventListener('click', async () => {
            title = document.querySelector('.job-search-bar').value;
            console.log(title)
            location = document.querySelector('.job-location-filter').value;
            date = getSelectedRadioValue();
            console.log(date)
            jobs = []
            currentOffset = 0
            const jobsData = await fetchJobData(title, location, date); // Fetch jobs with pagination
            document.querySelector('.js-job-card-section').innerHTML = ''
            // window.location.href = url
            displayJobs(jobsData['jobs'], jobsData['jobCount'])
            currentOffset += limit;
            document.querySelector('.js-expand-more-filters').style.display = 'none'
        })
    
    })
   

// Initial Load
loadMoreJobs();

// Infinite scroll event listener
window.addEventListener('scroll', () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
        // If the user is near the bottom, load more jobs
        // console.log(title)
        loadMoreJobs(title, location, date, sortValue);
    }
});

dropdown.addEventListener('change', async() => {
    document.querySelector('.js-job-card-section').innerHTML = ''
    sortValue = dropdown.value;
    // console.log(sortValue)
    currentOffset = 0
    jobs = [] //This ensures thatjobs have the right index when clicked
    await loadMoreJobs(title, location, date, sortValue)
})




const moreFilters = document.querySelector('.js-expand-more-filters')
moreFilters.style.display = 'none';
document.querySelector('.js-more-filters')
    .addEventListener('click', () => {
        moreFilters.style.display === 'none' ? moreFilters.style.display = 'block' : moreFilters.style.display ='none'
    })

document.querySelector('.js-more-filter-close')
    .addEventListener('click', () => {
        moreFilters.style.display = 'none'
    })



let jobId;

// Function to fetch job details based on jobId
const fetchJob = async () => {
    const response = await fetch(`http://127.0.0.1:8000/job/${jobId}`);
    return await response.json(); 
};

// Event listener for click on job cards
document.addEventListener('click', async (event) => {
    const isMobile = window.matchMedia("(max-width: 767px)").matches;
    
    // Ensure we clicked on a job card
    const jobCard = event.target.closest('.job-card');
    if (jobCard) {
        // Get the job index from the job cards array
        const jobIndex = Array.from(document.querySelectorAll('.job-card')).indexOf(jobCard);
        
        if (isMobile) {
            // On mobile: Redirect to a new page with jobId in the URL
            window.location.href = `apply.html?jobId=${jobs[jobIndex].Id}`;
        } else {
            document.querySelector('.js-main-big-job-posting').innerHTML = "";
            document.querySelector('.js-big-similar-job-card-section').innerHTML = "";
            // On desktop: Update jobId and fetch job data
            jobId = jobs[jobIndex].Id; // Ensure `jobs` contains your job data array with Ids
            const job = await fetchJob(); // Fetch job data
            
            // Render job details on the page
            const applyHTML = `
                <div class="apply-header">
                    <img class="apply-company-logo js-apply-company-logo" src="${job.CompanyLogo}" height="80px" width="80px">
                    <h5 class="apply-company-name js-apply-company-name">${job.CompanyName}</h5>
                </div>
                <h1 class="job-title js-job-title">${job.Title}</h1>
                <div class="job-description js-job-description">
                    <p>${job.Description}</p>
                </div>

            `;
            document.querySelector('.js-main-big-job-posting').innerHTML = applyHTML;

            const fetchSimilarJob = async (jobId) => {
                const response = await fetch(`http://127.0.0.1:8000/job/similar/${jobId}`);
                return await response.json() 
            
            } 

            const similarJobs = await fetchSimilarJob(jobId); // Await the fetching of job data
            console.log(similarJobs)

            // Store the fetched jobs in the globally accessible jobs array
            similarJobsList.push(...similarJobs.results); // Append new jobs to the jobs array
            console.log("Similar List", similarJobsList)

            let similarJobsHTML = '';

            similarJobs['results'].forEach((job) => { // Iterate through the jobs and create HTML for each
                similarJobsHTML += `
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
           
            document.querySelector('.js-big-similar-job-card-section').innerHTML += similarJobsHTML; // Insert the job cards into the DOM
            similarJobsList = []
            
        }
    }
});

