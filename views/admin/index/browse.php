<?php $title = __('OCR');?>
<?php echo head(array('title' => __('OCR'), 'bodyclass' => 'w3Page'));?>
<head>
    <script>
        window.onload = function() {
            var ocr = document.getElementById('ocr'); 
            ocr.onclick = ocrDocuments;
        };

        var ocrDocuments = function() {
            // TODO individual OCR jobs will time out.
            // Figure out how to extend the time limit for an Omeka PHP job.
            var details = document.getElementById('details');
            var start = document.getElementById('start').value;
            var end = document.getElementById('end').value;
            for (var i = start; i <= end; i++) {
                var data = {
                    'action': 'ocr',
                    'start': i,
                    'end': i + 1,
                    'url': "<?php echo rtrim(absolute_url(""), "admin/") ?>",
                    'api_key': document.getElementById('api_key').value
                };
                var status = document.getElementById('status');
                status.innerHTML = '<strong>Status: In progress.</strong>';
                status.style.display = 'block';
                jQuery.post('/admin/ocr/index/ocr', data, function (response) {
                    details.innerHTML = response;
                    status.innerHTML = '<strong>Status: Done running OCR.';
                    var expander = document.getElementById('details_expander');
                    expander.style.display = 'block';
                    expander.onclick = function() {
                        if (details.style.display === 'none') {
                            details.style.display = 'block';
                        } else {
                            details.style.display = 'none';
                        }
                    };
                });
            }
        };
    </script>
</head>
<body>
    <p>
        Enter your OCR API key below. 
        Then enter a range of documents to be OCRed, e.g., documents 1 through 10.
        The OCR process may take a while.
        <strong>Warning: Currently, many OCR jobs will not complete because they take too long.</strong>
    </p>
    <input type="text" placeholder="OCR API key" id="api_key"/>
    <input type="number" placeholder="Start ID" id="start"/>
    <input type="number" placeholder="End ID" id="end"/>
    <button id="ocr">OCR Documents</button> 
    <p id="status" style="display: none;"></p>
    <button id="details_expander" style="display: none;">Display Details</button>
    <pre id="details" style="display: none;"></pre>
</body>

