export async function generateCourse(brief=null){

    const response = await fetch("/.netlify/functions/generate-course",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({ brief })
    })

    const data = await response.json()

    if(!response.ok){
        console.error(data)
        alert("Course generation failed.")
        return
    }

    console.log(data)
    alert("Course generation complete.")
}