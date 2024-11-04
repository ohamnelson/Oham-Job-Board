const params = new URLSearchParams(window.location.search);
const jobId = params.get('jobId');


const fetchJob = async () => {
    const response = await fetch(`http://127.0.0.1:8000/job/${jobId}`);
    return await response.json() 

} 
const job = await fetchJob(); // Await the fetching of job data

// Render job details
const applyHTML = `
<div class="apply-header">
    <img class="apply-company-logo js-apply-company-logo" src="${job.CompanyLogo}" height="100px" width="100px">
    <h5 class="apply-company-name js-apply-company-name">${job.CompanyName}</h5>
</div>`;
document.querySelector('.apply-header').innerHTML = applyHTML;
document.querySelector('.js-job-title').innerHTML = job.Title
document.querySelector('.js-job-description').innerHTML = job.Description;

