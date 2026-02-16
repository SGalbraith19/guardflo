document.getElementById("exportPdf").onclick = () => {
 const win = window.open("", "_blank");
 win.document.write(`
   <html>
     <head>
       <title>GuardFlo — System Response</title>
       <style>
         body {
           font-family: -apple-system, sans-serif;
           background: #f4f7fb;
           padding: 40px;
         }
         .card {
           background: rgba(255,255,255,0.8);
           padding: 24px;
           border-radius: 18px;
         }
       </style>
     </head>
     <body>
       <div class="card">
         <h1>System Response</h1>
         <pre>${response-box.textContent}</pre>
       </div>
     </body>
   </html>
 `);
 win.print();
};