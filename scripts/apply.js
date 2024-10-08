const params = new URLSearchParams(window.location.search);
const jobId = params.get('jobId');


const fetchJob = async () => {
    const response = await fetch(`http://127.0.0.1:8000/job/${jobId}`);
    return await response.json() 

} 
const job = await fetchJob(); // Await the fetching of job data

// Render job details
document.querySelector('.js-job-title').innerHTML = job.Title
document.querySelector('.js-job-description').innerHTML = job.Description;


