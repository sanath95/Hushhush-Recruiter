# <div style="text-align: center;">Group 12 - User Stories<div>

### Table of contents
1. [Recruiter User Story](#recruiter-user-story)
2. [Candidate User Story](#candidate-user-story)
3. [HR User Story](#hr-user-story)

---

### Recruiter User Story

As a recruiter of Doodle, 
- I wish to automate the process of candidate selection using an in-house solution for different job roles
- I would like to notify the prospective candidates about the job opportunity
- I would like to get the candidate's answers automatically evaluated (using existing neural networks, sonarqube, etc)
- I would like to give feedback to the candidate about the results along with a report.

### <div style="text-align: center; text-decoration: underline;" >Candidate Selection</div>

```mermaid
flowchart TD
    user([Recruiter])
    openapp[Open application]
    selectrequirements[Select job roles / job description]
    selectn[Select n number of candidates to see]
    listofcandidates[Get list of prospective candidates]
    flagcandidates[Flag candidates]
    selectcandidates[Select candidates]
    notifyhr[Notify the HR about selected candidates]
    candidatenotified([HR will notify the candidates])

    user --> openapp
    openapp --> selectrequirements
    selectrequirements --> selectn
    selectn --> listofcandidates
    listofcandidates --> flagcandidates
    flagcandidates --> selectcandidates
    listofcandidates --> selectcandidates
    selectcandidates --> notifyhr
    notifyhr --> candidatenotified
```

> Flagged candidates will not appear in the list in the future!

### <div style="text-align: center; text-decoration: underline;">Candidate Evaluation</div>

```mermaid
flowchart TD
    user([Recruiter])
    answered{Coding test accepted?}

    receiverejectresponse([Receive response that test was rejected])
    receiveacceptedresponse[Receive response that test was accepted]
    receiveanswers[Receive evaluated results of candidates]
    checkanswers[Check candidates answers]
    feedbackreport[Prepare feedback report]
    notifyhr[Notify HR about the results]
    notifycandidates([HR gives feedback to candidate])

    user --> answered
    answered --> |No| receiverejectresponse
    answered --> |Yes| receiveacceptedresponse
    receiveacceptedresponse --> receiveanswers
    receiveanswers --> checkanswers
    checkanswers --> feedbackreport
    receiveanswers --> feedbackreport
    feedbackreport --> notifyhr
    notifyhr --> notifycandidates
```

---

### Candidate User Story

As a prospective candidate for the job at Doodle,
- I wish to get notified when I'm selected for the coding test
- I would like to submit my answers online
- I would like to receive a feedback for the coding test
- I would like to be able to contact the HR if I have any queries
- I would like to see the status of my coding test on the platform.

### <div style="text-align: center; text-decoration: underline;">Coding Test</div>

```mermaid
flowchart TD
    user([Candidate])
    receivenotification[Receive invite for the coding test]
    acceptorreject{Accept the coding test?}
    reject([Reject the test and notify HR and recruiter])
    accept[Click on link]
    codingtest[Answer coding questions]
    submit[Submit]
    checkstatus[Check status]
    messagehr[Message HR]
    messageresponse[Response from HR]
    receivefeedback([Feedback for coding test])

    user --> receivenotification
    receivenotification --> acceptorreject
    acceptorreject --> |No| reject
    acceptorreject --> |Yes| accept
    accept --> codingtest
    codingtest --> submit
    submit --> checkstatus
    submit --> messagehr
    checkstatus --> receivefeedback
    messagehr --> messageresponse
    messageresponse --> messagehr
    messageresponse --> receivefeedback
```

---

### HR User Story

As a HR at Doodle,
- I wish to communicate with the candidate about being selected for the coding test
- I would like to provide feedback to the candidate about the coding test results
- I would like to be able to update the application status on the platform
- I would like to be able to communicate with the candidate if they have any queries.

### <div style="text-align: center; text-decoration: underline;">Status Update</div>

```mermaid
flowchart LR
    user([HR])
    openapp[Open application]
    updatestatus([Update candidate status])

    user --> openapp
    openapp --> updatestatus
```

> Status options: 1) Selected, 2) Rejected/Accepted, 3) Under Evaluation, 4) Fail/Pass

### <div style="text-align: center; text-decoration: underline;">Candidate Queries</div>

```mermaid
flowchart LR
    user([HR])
    openapp[Open application]
    receivemessage[Receive message from candidate]
    respondmessage[Respond to the candidate]
    closesession([Close the chat session])

    user --> openapp
    openapp --> receivemessage
    receivemessage --> respondmessage
    respondmessage --> receivemessage
    respondmessage --> closesession
```

---
---