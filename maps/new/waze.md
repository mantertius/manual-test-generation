# Test Case Suite for Navigation Instructions Screenshot

### Test Case 1: Verify Default State of Interface

#### Preconditions: 
- The map application is open and displays the navigation instructions panel.

| Step | Actions | Verifications |
|------|---------|---------------|
| 1    | Launch the map application. | The map should be displayed with the navigation instruction panel shown in the screenshot. |
| 2    | Observe the "Escolha o ponto de partida" field. | The field should be empty, with placeholder text "Escolha o ponto de partida". |
| 3    | Observe the "Escolha o destino" field. | The field should be empty, with placeholder text "Escolha o destino". |
| 4    | Check the "Saia agora" dropdown menu. | Default option should be visible as "Saia agora". |
| 5    | Check the map for traffic alerts and navigation icons. | Various icons should be displayed on the map indicating traffic incidents and points of interest. |

### Test Case 2: Input Starting Point and Destination

#### Preconditions: 
- The map application is open and displays the navigation instructions panel.

| Step | Actions | Verifications |
|------|---------|---------------|
| 1    | Click on the "Escolha o ponto de partida" field. | The field should become active with a blinking cursor. |
| 2    | Enter a starting point (e.g., "New York City"). | The entered text should be displayed in the field. |
| 3    | Click on the "Escolha o destino" field. | The field should become active with a blinking cursor. |
| 4    | Enter a destination (e.g., "Central Park"). | The entered text should be displayed in the field. |
| 5    | Verify that route options are updated based on the input. | Route suggestions should appear on the map and in the panel if the entered locations are valid. |

### Test Case 3: Check Navigation Icons and Alerts

#### Preconditions: 
- The map application is open and displays the navigation instructions panel.

| Step | Actions | Verifications |
|------|---------|---------------|
| 1    | Locate navigation icons on the map. | Icons should be clearly visible and identifiable. |
| 2    | Click on a traffic congestion icon. | Detailed information about the congestion should appear. |
| 3    | Click on a speed camera icon. | Detailed information about the speed camera should appear. |
| 4    | Click on a hazard warning icon. | Detailed information about the hazard should appear. |

### Test Case 4: Log In Functionality

#### Preconditions: 
- The map application is open and displays the navigation instructions panel.

| Step | Actions | Verifications |
|------|---------|---------------|
| 1    | Click on the "Entrar" button. | Log in interface should open. |
| 2    | Enter valid user credentials. | The fields should accept the input and allow the form to be submitted. |
| 3    | Submit the log-in form. | The user should be logged in and taken back to the map interface. |
| 4    | Verify that the user name or profile icon is displayed. | The name/icon should appear, indicating a successful login. |

### Test Case 5: Change Departure Time

#### Preconditions: 
- The map application is open and displays the navigation instructions panel.

| Step | Actions | Verifications |
|------|---------|---------------|
| 1    | Click on the "Saia agora" dropdown. | A list of options should be displayed. |
| 2    | Select a different departure time (e.g., "Saia em 30 minutos"). | The selected option should reflect the chosen departure time. |
| 3    | Confirm that the route suggestions are updated based on the new departure time. | The routes displayed on the map and in the panel should update accordingly. |

---
[SYSTEM]: You are a specialist in manual natural language tests. You need to test different functionalities. You cannot create similar test cases. The test cases should be detailed and cover both basic functionality and potential edge cases to ensure comprehensive testing. Follow a professional and clear style guide. First step is to analyze the picture, then write the test cases. Third step is to rewrite similar test cases to avoid similarities.

[USER]: Create a manual test case suite with 5 test cases for the provided screenshot, where each test will have different objectives. Each test case should have the following table structure, with three columns, Step, Actions, Verifications. Also, add a title to each table. Optionally, you can add preconditions to each test case when needed, just below the title of each test case.

 Image: [https://drive.google.com/uc?export=download&id=1i7Wry6GJeSTjQTptzQM_Jl9AMo3Lmbm-](https://drive.google.com/uc?export=download&id=1i7Wry6GJeSTjQTptzQM_Jl9AMo3Lmbm-)
