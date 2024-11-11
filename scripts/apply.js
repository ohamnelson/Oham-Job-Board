const params = new URLSearchParams(window.location.search);
const jobId = params.get('jobId');

let similarJobsList = []
console.log(jobId)


const fetchJob = async () => {
    const response = await fetch(`http://127.0.0.1:8000/job/${jobId}`);
    return await response.json() 

} 
const job = await fetchJob(); // Await the fetching of job data
console.log(job)

// Render job details
const applyHTML = `
<div class="apply-header">
    <img class="apply-company-logo js-apply-company-logo" src="${job.CompanyLogo}" height="100px" width="100px">
    <h5 class="apply-company-name js-apply-company-name">${job.CompanyName}</h5>
</div>`;
document.querySelector('.apply-header').innerHTML = applyHTML;
document.querySelector('.js-job-title').innerHTML = job.Title
document.querySelector('.js-job-description').innerHTML = job.Description;

const fetchSimilarJob = async (jobId) => {
    const response = await fetch(`http://127.0.0.1:8000/job/similar/${jobId}`);
    return await response.json() 

} 
const similarJobs = await fetchSimilarJob(jobId); // Await the fetching of job data
console.log(similarJobs)

 // Store the fetched jobs in the globally accessible jobs array
 similarJobsList.push(...similarJobs.results); // Append new jobs to the jobs array

let jobsHTML = '';

similarJobs['results'].forEach((job) => { // Iterate through the jobs and create HTML for each
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

document.querySelector('.js-similar-job-card-section').innerHTML += jobsHTML; // Insert the job cards into the DOM

// Event listeners for job card click
document.addEventListener('click', (e) => {
    if (e.target.closest('.job-card')) {
        const jobCard = e.target.closest('.job-card');
        const jobIndex = Array.from(document.querySelectorAll('.job-card')).indexOf(jobCard);
        window.location.href = `apply.html?jobId=${similarJobsList[jobIndex].Id}`;
    }
});