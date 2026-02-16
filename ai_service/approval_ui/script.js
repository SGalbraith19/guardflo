async function loadRecommendations() {
 const res = await fetch("http://localhost:9001/recommendations");
 const data = await res.json();

 const container = document.getElementById("recommendations");
 container.innerHTML = "";

 if (data.length === 0) {
   container.innerHTML = "<p>No recommendations available.</p>";
   return;
 }

 data.forEach(rec => {
   const div = document.createElement("div");
   div.className = "card";

   div.innerHTML = `
     <strong>Recommendation ID:</strong> ${rec.recommendation_id}<br/>
     <strong>Action:</strong> ${rec.proposal.action}<br/>
     <strong>Reason:</strong> ${rec.reasoning.explanation}<br/>
     <br/>
     <button class="approve">Approve</button>
     <button class="reject">Reject</button>
   `;

   div.querySelector(".approve").onclick = () =>
     submitDecision(rec.recommendation_id, "approved");

   div.querySelector(".reject").onclick = () =>
     submitDecision(rec.recommendation_id, "rejected");

   container.appendChild(div);
 });
}

async function submitDecision(recommendationId, decision) {
 await fetch("http://localhost:9001/approvals", {
   method: "POST",
   headers: { "Content-Type": "application/json" },
   body: JSON.stringify({
     recommendation_id: recommendationId,
     decision: decision,
     approved_by: "example-ui-user",
     approval_context: "demo-ui"
   })
 });

 alert(`Decision recorded: ${decision}`);
 loadRecommendations();
}

loadRecommendations();