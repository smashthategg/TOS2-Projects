function archiveOldResponses() {
  var sheet = SpreadsheetApp.openById('1IwhWyb4Ms0tuIBsWVI2ry2NiMj5CklJBR7d4NjUXAu4'); // Replace with your Google Sheets ID
  var mainSheet = sheet.getSheetByName("ToS2 Leaderboard Update Form");
  var archiveSheet = sheet.getSheetByName("Archived_Responses");

  // If we have responses for the week
  var lastRow = mainSheet.getLastRow();
  if (lastRow > 1) {
    // Get all data from the main sheet
    var range = mainSheet.getRange('A2:H' + lastRow);
    var values = range.getValues();

    // Archive the resposnes
    for (var row = 0; row < values.length; row++) {
        archiveSheet.insertRows(2)
        archiveSheet.getRange('A2:H2').setValues([values[row]]);
        mainSheet.deleteRow(2); // Delete row (row index in deleteRow is 1-based)
    }
    // Add row to archive sheet with current date  
    var currentDate = new Date();
    var formattedDate = Utilities.formatDate(currentDate, Session.getScriptTimeZone(), 'yyyy-MM-dd');

    archiveSheet.insertRows(2)
    archiveSheet.getRange('A2').setValues([["RESPONSES FOR " + formattedDate]]);
  }
}


var formId = '1zrmx0fT6H9ZKLdVyuj0j8JBGtBFy2pEme6ldwgwwdTk'; 
var form = FormApp.openById(formId);
var currentDate = new Date();

function openForm() {
  form.setAcceptingResponses(true); // Open the form
  Logger.log('Form opened on ' + currentDate)
}

function closeForm() {
  form.setAcceptingResponses(false); // Close the form
  Logger.log('Form closed on ' + currentDate)
}

function formatDate() {
  var sheet = SpreadsheetApp.openById('1IwhWyb4Ms0tuIBsWVI2ry2NiMj5CklJBR7d4NjUXAu4').getSheetByName("ToS2 Leaderboard Update Form");
  var range = sheet.getRange('A:A');  // Change to the range you need
  var dateFormat = 'YYYY-MM-DD';  // Custom date format
  range.setNumberFormat(dateFormat);
}
