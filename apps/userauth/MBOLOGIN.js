import React, { Component } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StatusBar,
  Alert,
  ActivityIndicator,
  Platform,
  Image,
  Dimensions,
  ScrollView,
} from 'react-native';
import SoapRequest from '../SoapRequest';
import { onSignIn, getLastUserLogin } from './Auth';
import { withNavigation } from 'react-navigation';
import {
  mbApiConfig,
  mbEndpoints,
  getClientRequiredFields,
  createUserAccount,
  buildV6ApiRequest,
  getClientsByEmail,
} from './api/Mindbody';
import { getUserInfo, setUserInfo } from '../../Constants';
import { refreshUserCache } from '../UserCache';
import firebase from '../../components/Firebase';
import * as LocalAuthentication from 'expo-local-authentication';
import Assets from '../../assets/Assets';
import { styles } from './LoginForm.style';

class LoginForm extends Component {
  state = {
    email: '',
    password: '',
    userId: null,
    loading: false,
    forgotPassword: false,
    signUp: false,
    enrolled: false,
    enrollmentType: null,
    requiredFields: [],
  };

  constructor(props) {
    super(props);
    this.db = firebase.firestore();
    this.prefDbRef = this.db.collection('userPreferences');
    this.userInfoRef = this.db.collection('userInfo');
  }

  componentDidMount() {
    this.checkLocalAuthentication();
  }

  checkLocalAuthentication = async () => {
    let pass = false;
    let lastUserLogin = null;
    let enrolled = false;
    let enrollmentType = null;
    try {
      lastUserLogin = await getLastUserLogin();
      if (lastUserLogin) {
        // Check for local authentication.
        //if(Platform.OS === 'ios'){
        let result = await LocalAuthentication.hasHardwareAsync();
        console.log('Has Authentication Hardware?', result);

        // Get supported authentication types
        if (result) {
          let authTypes = await LocalAuthentication.supportedAuthenticationTypesAsync();
          // We have at least one authentication type.
          if (authTypes && authTypes.length > 0) {
            console.log(authTypes);
            for (let i = 0; i < authTypes.length; i++) {
              if (authTypes[i] === LocalAuthentication.AuthenticationType.FINGERPRINT) {
                enrollmentType = LocalAuthentication.AuthenticationType.FINGERPRINT;
              } else if (authTypes[i] === LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION) {
                enrollmentType = LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION;
              }
            }

            // Check for enrollment.
            enrolled = await LocalAuthentication.isEnrolledAsync();
          }
        }
        //}
      }
    } catch (error) {
      console.log('An error occurred while checking for local authentication enrollment', error);
    }

    this.setState({ enrolled: enrolled, enrollmentType: enrollmentType });
  };

  showAndroidAlert = () => {
    Alert.alert('Fingerprint Scan', 'Press SCAN and then immediately place your finger over the touch sensor.', [
      {
        text: 'Scan',
        onPress: () => {
          this.authenticateLocal();
        },
      },
      { text: 'Cancel', onPress: () => console.log('Cancel'), style: 'cancel' },
    ]);
  };

  authenticateLocal = async () => {
    let pass = false;
    let lastUserLogin = null;

    try {
      let result = await LocalAuthentication.authenticateAsync();
      console.log(result);
      if (result.success) {
        pass = true;
      } else {
        Alert.alert('Login Error', 'An error occurred while logging in.\r\n\r\nPlease try again.', [
          { text: 'OK', style: 'cancel' },
        ]);
      }

      lastUserLogin = await getLastUserLogin();

      if (pass && lastUserLogin) {
        let tokenSplitIndex = lastUserLogin.indexOf('|!|');
        //console.log(tokenSplitIndex)
        if (tokenSplitIndex != -1) {
          let email = lastUserLogin.substring(0, tokenSplitIndex);
          let password = lastUserLogin.substring(tokenSplitIndex + 3, lastUserLogin.length);
          this.setState({ email, password });
          this.state.email = email;
          //console.log('Local authentication with ', email, password);
          this.login();
        }
      }
    } catch (errors) {
      console.log('An error occurred while authenticating locally', error);
    }
  };

  fetchClientRecordByEmail = async email => {
    return await getClientsByEmail(email);
  };

  getUserDoc = async userId => {
    const userRef = this.userInfoRef.doc(`${userId}`);
    const docSnapshot = await userRef.get();
    if (docSnapshot.exists) {
      return docSnapshot.data();
    } else {
      return {};
    }
  };

  showDisabledAlert = async () => {
    Alert.alert(
      'Inactive Account',
      'Your account is currently inactive.\r\n\r\nTo gain access to FTF360 you must be an active client.',
      [
        {
          text: 'OK',
          onPress: async () => {},
          style: 'confirm',
        },
      ],
      { cancelable: true },
    );
    this.setState({ loading: false });
  };

  login = async () => {
    const { email, password } = this.state;
    try {
      if (email.trim().length == 0 || password.trim().length == 0) {
        Alert.alert('Something Went Wrong', 'Please enter your e-mail and password.', [{ text: 'OK' }], {
          cancelable: true,
        });
        return;
      }

      this.setState({ loading: true });

      if (this.props.onLogin) {
        this.props.onLogin();
      }

      // First check user login
      const soapRequest = new SoapRequest({
        targetNamespace: mbEndpoints.namespace,
        requestURL: mbEndpoints.clientService,
      });

      soapRequest.createRequest({
        'ch0:ValidateLogin': {
          'ch0:Request': {
            'ch0:SourceCredentials': {
              'ch0:SourceName': mbApiConfig.credentials.sourceUserName,
              'ch0:Password': mbApiConfig.credentials.sourcePassword,
              'ch0:SiteIDs': {
                'ch0:int': mbApiConfig.credentials.siteId,
              },
            },
            'ch0:Username': email,
            'ch0:Password': password,
          },
        },
      });

      const foundClients = await this.fetchClientRecordByEmail(email);
      console.info('foundClients', foundClients);
      if (foundClients && foundClients.length > 0) {
        if (!foundClients[0].Active) {
          this.showDisabledAlert();
          return;
        }

        const userId = foundClients[0].Id;
        const { deleted } = await this.getUserDoc(userId);
        if (deleted) {
          this.showDisabledAlert();
          return;
        }
      }

      let result = await soapRequest.sendRequest(mbEndpoints.loginAction);
      if (result && result['soap:Envelope'] && result['soap:Envelope']['soap:Body']) {
        var validateLoginResult =
          result['soap:Envelope']['soap:Body'][0]['ValidateLoginResponse'][0]['ValidateLoginResult'][0];

        // Check for client
        if (validateLoginResult['Status'] && validateLoginResult['Status'][0] === 'Success') {
          let clientId = validateLoginResult['Client'][0]['ID'][0] + '';
          await this.fetchClientRecord2(clientId);

          // Check for inactive
          if (/*getUserInfo().active*/ true) {
            await onSignIn(clientId, email, password);
            await this.getClientAnniversary(clientId);
            this.props.navigation.navigate('AuthLoading');
            return;
          } else {
            // User is inactive so show them a warning.
            this.setState({ loading: false });

            // if(clientId === '23932310108'){
            //     if(soundObject){
            //         await soundObject.unloadAsync();
            //     }
            //     else{
            //         soundObject = new Audio.Sound();
            //     }
            //     await soundObject.loadAsync(require('../../assets/sounds/magicwrd.wav'));
            //     await soundObject.setIsLoopingAsync(true);
            //     await soundObject.playAsync();
            // }

            Alert.alert(
              'Inactive Account',
              'Your account is currently inactive.\r\n\r\nTo gain access to FTF360 you must be an active client.',
              [
                {
                  text: 'OK',
                  onPress: async () => {
                    // if(soundObject){
                    //     await soundObject.unloadAsync();
                    // }
                  },
                  style: 'confirm',
                },
              ],
              { cancelable: true },
            );
            return;
          }
        } else {
          // User login failed, maybe it is a staff member
          const soapRequestStaff = new SoapRequest({
            targetNamespace: mbEndpoints.namespace,
            requestURL: mbEndpoints.staffService,
          });
          soapRequestStaff.createRequest({
            'ch0:ValidateStaffLogin': {
              'ch0:Request': {
                'ch0:SourceCredentials': {
                  'ch0:SourceName': mbApiConfig.credentials.sourceUserName,
                  'ch0:Password': mbApiConfig.credentials.sourcePassword,
                  'ch0:SiteIDs': {
                    'ch0:int': mbApiConfig.credentials.siteId,
                  },
                },
                'ch0:Username': email,
                'ch0:Password': password,
              },
            },
          });

          result = await soapRequestStaff.sendRequest(mbEndpoints.loginStaffAction);
          if (result && result['soap:Envelope'] && result['soap:Envelope']['soap:Body']) {
            var validateStaffLoginResult =
              result['soap:Envelope']['soap:Body'][0]['ValidateStaffLoginResponse'][0]['ValidateStaffLoginResult'][0];

            if (validateStaffLoginResult['Status'] && validateStaffLoginResult['Status'][0] === 'Success') {
              let clientId = validateStaffLoginResult['Staff'][0]['ID'][0] + '';
              let accessLevel = validateStaffLoginResult['Staff'][0]['UserAccessLevel'][0];
              if (accessLevel === 'Owner') {
                let staffEntry = validateStaffLoginResult['Staff'][0];
                staffEntry.userId = parseInt(staffEntry['ID'][0]);
                staffEntry.mobilePhone = staffEntry['MobilePhone'][0];
                staffEntry.email = staffEntry['Email'][0];
                staffEntry.name = `${staffEntry['FirstName'][0]} ${staffEntry['LastName'][0]}`;
                staffEntry.photoUrl = null;
                staffEntry.isStaff = true;

                // Default preferences
                staffEntry.preferences = {
                  userId: staffEntry.userId,
                  alertsEnabled: true,
                  sessionReminder: false,
                  mealOrderReminder: true,
                  chargeMyZoneReminder: true,
                  clientLevelTestingReminder: true,
                  preferredCalendar: 'default',
                  childCarePrompt: false,
                  accountabilityPrompt: false,
                  remoteClassPrompt: true,
                };

                await this.handlePreferences(staffEntry);
                await refreshUserCache(JSON.stringify(staffEntry));
                setUserInfo(staffEntry);
                await onSignIn(clientId, email, password);
                if (this.props.screenProps.appDisplayed) {
                  this.props.screenProps.appDisplayed();
                }
                this.props.navigation.navigate('StaffApp');

                return;
              } else {
                await onSignIn(clientId, email, password);
                await this.fetchStaffRecord(clientId);
                if (this.props.screenProps.appDisplayed) {
                  this.props.screenProps.appDisplayed();
                }
                this.props.navigation.navigate('StaffApp');

                return;
              }
            } else {
              this.setState({ loading: false });
              Alert.alert('Something Went Wrong', validateLoginResult['Message'][0], [{ text: 'OK' }], {
                cancelable: true,
              });
            }
          }
        }
      }
    } catch (error) {
      console.log(error);
    }
  };

  fetchClientRecord(userId) {
    const that = this;
    const soapRequest = new SoapRequest({
      targetNamespace: mbEndpoints.namespace,
      requestURL: mbEndpoints.clientService,
    });

    soapRequest.createRequest({
      'ch0:GetClients': {
        'ch0:Request': {
          'ch0:SourceCredentials': {
            'ch0:SourceName': mbApiConfig.credentials.sourceUserName,
            'ch0:Password': mbApiConfig.credentials.sourcePassword,
            'ch0:SiteIDs': {
              'ch0:int': mbApiConfig.credentials.siteId,
            },
          },
          'ch0:UserCredentials': {
            'ch0:Username': mbApiConfig.credentials.staffUserName,
            'ch0:Password': mbApiConfig.credentials.staffPassword,
            'ch0:SiteIDs': {
              'ch0:int': mbApiConfig.credentials.siteId,
            },
          },
          'ch0:ClientIDs': {
            'ch0:string': userId,
          },
          'ch0:Fields': [{ 'ch0:string': 'Clients.CustomClientFields' }, { 'ch0:string': 'Clients.ClientCreditCard' }],
        },
      },
    });

    return soapRequest.sendRequest(mbEndpoints.getClientsAction).then(result => {
      let response = result['soap:Envelope']['soap:Body'][0]['GetClientsResponse'][0]['GetClientsResult'][0];
      console.log(response);
      if (response['Status'][0] === 'Success') {
        if (response['ResultCount'][0] == 1) {
          let clientEntry = response['Clients'][0]['Client'][0];

          // Grab the MyZone belt and virtual client.
          clientEntry.myZoneBeltId = null;
          clientEntry.virtualClient = false;
          if (
            clientEntry['CustomClientFields'] &&
            clientEntry['CustomClientFields'].length > 0 &&
            clientEntry['CustomClientFields'][0]
          ) {
            for (var i = 0; i < clientEntry['CustomClientFields'].length; i++) {
              if (
                clientEntry['CustomClientFields'][i] &&
                clientEntry['CustomClientFields'][i]['CustomClientField'] &&
                clientEntry['CustomClientFields'][i]['CustomClientField'][0]
              ) {
                let customField = clientEntry['CustomClientFields'][i]['CustomClientField'][0];
                if (customField['Name'][0] === 'MyZone Belt') {
                  clientEntry.myZoneBeltId = customField['Value'][0];
                  clientEntry.myZoneUserGUID = null;
                } else if (customField['Name'][0] === 'Virtual Client Start Date') {
                  if (customField['Value'][0] && customField['Value'][0].length > 0) {
                    clientEntry.virtualClient = true;
                  }
                }
              }
            }
          }

          // Grab the client id, cell phone and image
          clientEntry.userId = parseInt(clientEntry['ID'][0]);
          clientEntry.mobilePhone = clientEntry['MobilePhone'] ? clientEntry['MobilePhone'][0] : '';
          clientEntry.email = clientEntry['Email'][0];
          clientEntry.name = `${clientEntry['FirstName'][0]} ${clientEntry['LastName'][0]}`;
          clientEntry.address = clientEntry['AddressLine1'] ? clientEntry['AddressLine1'][0] : '';
          clientEntry.city = clientEntry['City'] ? clientEntry['City'][0] : '';
          clientEntry.state = clientEntry['State'] ? clientEntry['State'][0] : '';
          clientEntry.zip = clientEntry['PostalCode'] ? clientEntry['PostalCode'][0] : '';

          if (clientEntry['Status'] && clientEntry['Status'].length > 0 && clientEntry['Status'][0]) {
            clientEntry.active = clientEntry['Status'][0].toLowerCase() === 'active';
          } else {
            clientEntry.active = true;
          }

          if (clientEntry['PhotoURL'] && clientEntry['PhotoURL'].length > 0 && clientEntry['PhotoURL'][0]) {
            clientEntry.photoUrl = clientEntry['PhotoURL'][0];
          } else {
            clientEntry.photoUrl = null;
          }
          clientEntry.isStaff = false;

          // Credit card info.
          clientEntry.payment = null;
          if (
            clientEntry['ClientCreditCard'] &&
            clientEntry['ClientCreditCard'].length > 0 &&
            clientEntry['ClientCreditCard'][0]
          ) {
            let payment = {
              cardType: clientEntry['ClientCreditCard'][0]['CardType']
                ? clientEntry['ClientCreditCard'][0]['CardType'][0]
                : '',
              lastFour: clientEntry['ClientCreditCard'][0]['LastFour']
                ? clientEntry['ClientCreditCard'][0]['LastFour'][0]
                : '',
              cardHolder: clientEntry['ClientCreditCard'][0]['CardHolder']
                ? clientEntry['ClientCreditCard'][0]['CardHolder'][0]
                : '',
              expMonth: clientEntry['ClientCreditCard'][0]['ExpMonth']
                ? clientEntry['ClientCreditCard'][0]['ExpMonth'][0]
                : '',
              expYear: clientEntry['ClientCreditCard'][0]['ExpYear']
                ? clientEntry['ClientCreditCard'][0]['ExpYear'][0]
                : '',
              address: clientEntry['ClientCreditCard'][0]['Address']
                ? clientEntry['ClientCreditCard'][0]['Address'][0]
                : '',
              city: clientEntry['ClientCreditCard'][0]['City'] ? clientEntry['ClientCreditCard'][0]['City'][0] : '',
              state: clientEntry['ClientCreditCard'][0]['State'] ? clientEntry['ClientCreditCard'][0]['State'][0] : '',
              postalCode: clientEntry['ClientCreditCard'][0]['PostalCode']
                ? clientEntry['ClientCreditCard'][0]['PostalCode'][0]
                : '',
            };
            clientEntry.payment = payment;
          }

          // Default preferences
          clientEntry.preferences = {
            userId: clientEntry.userId,
            alertsEnabled: true,
            sessionReminder: false,
            mealOrderReminder: true,
            chargeMyZoneReminder: true,
            clientLevelTestingReminder: true,
            preferredCalendar: 'default',
            childCarePrompt: true,
            accountabilityPrompt: true,
            remoteClassPrompt: true,
          };

          // REMOVE
          //clientEntry.userId = 100000004;
          //clientEntry.isStaff = true;
          // REMOVE

          setUserInfo(clientEntry);

          this.handlePreferences(clientEntry).then(result => {
            refreshUserCache(JSON.stringify(clientEntry)).then(res => {
              setUserInfo(clientEntry);
              //setupPreferenceNotifications();
            });
          });
        }
      }
    });
  }

  fetchClientRecord2 = async userId => {
    try {
      let requestUrl = `${mbApiConfig.urls.apiBaseV6}client/clients`;
      requestUrl += `?ClientIds=${userId}`;

      let response = await buildV6ApiRequest(requestUrl, 'GET', true);

      if (!response.Error) {
        if (response.PaginationResponse && response.PaginationResponse.PageSize > 0) {
          let searchResults = response.Clients;
          if (searchResults?.length == 1) {
            let clientEntry = searchResults[0];

            // Custom fields (MyZone and Virtual).
            clientEntry.myZoneBeltId = null;
            clientEntry.virtualClient = false;
            if (clientEntry.CustomClientFields && clientEntry.CustomClientFields.length > 0) {
              for (let i = 0; i < clientEntry.CustomClientFields.length; i++) {
                let customField = clientEntry.CustomClientFields[i];
                if (
                  customField &&
                  customField.Name &&
                  customField.Name.length > 0 &&
                  customField.Name.toLowerCase() === 'myzone belt'
                ) {
                  clientEntry.myZoneBeltId = customField.Value;
                } else if (
                  customField &&
                  customField.Name &&
                  customField.Name.length > 0 &&
                  customField.Name.toLowerCase() === 'virtual client start date' &&
                  customField.Value?.length > 0
                ) {
                  clientEntry.virtualClient = true;
                }
              }
            }

            // Basics
            clientEntry.userId = parseInt(clientEntry.Id);
            clientEntry.mobilePhone = clientEntry.MobilePhone ? clientEntry.MobilePhone : '';
            clientEntry.email = clientEntry.Email;
            clientEntry.name = `${clientEntry.FirstName} ${clientEntry.LastName}`;
            clientEntry.address = clientEntry.AddressLine1 ? clientEntry.AddressLine1 : '';
            clientEntry.city = clientEntry.City ? clientEntry.City : '';
            clientEntry.state = clientEntry.State ? clientEntry.State : '';
            clientEntry.zip = clientEntry.PostalCode ? clientEntry.PostalCode : '';

            if (clientEntry.Status && clientEntry.Status.length > 0) {
              clientEntry.active = clientEntry.Status.toLowerCase() === 'active';
            } else {
              clientEntry.active = true;
            }

            if (clientEntry.PhotoUrl && clientEntry.PhotoUrl.length > 0) {
              clientEntry.photoUrl = clientEntry.PhotoUrl;
            } else {
              clientEntry.photoUrl = null;
            }
            clientEntry.isStaff = false;

            // Credit card info.
            clientEntry.payment = null;
            if (clientEntry.ClientCreditCard) {
              let payment = {
                cardType: clientEntry.ClientCreditCard.CardType ? clientEntry.ClientCreditCard.CardType : '',
                lastFour: clientEntry.ClientCreditCard.LastFour ? clientEntry.ClientCreditCard.LastFour : '',
                cardHolder: clientEntry.ClientCreditCard.CardHolder ? clientEntry.ClientCreditCard.CardHolder : '',
                expMonth: clientEntry.ClientCreditCard.ExpMonth ? clientEntry.ClientCreditCard.ExpMonth : '',
                expYear: clientEntry.ClientCreditCard.ExpYear ? clientEntry.ClientCreditCard.ExpYear : '',
                address: clientEntry.ClientCreditCard.Address ? clientEntry.ClientCreditCard.Address : '',
                city: clientEntry.ClientCreditCard.City ? clientEntry.ClientCreditCard.City : '',
                state: clientEntry.ClientCreditCard.State ? clientEntry.ClientCreditCard.State : '',
                postalCode: clientEntry.ClientCreditCard.PostalCode ? clientEntry.ClientCreditCard.PostalCode : '',
              };
              clientEntry.payment = payment;
            }

            // Default preferences
            clientEntry.preferences = {
              userId: clientEntry.userId,
              alertsEnabled: true,
              sessionReminder: false,
              mealOrderReminder: true,
              chargeMyZoneReminder: true,
              clientLevelTestingReminder: true,
              preferredCalendar: 'default',
              childCarePrompt: true,
              accountabilityPrompt: true,
              remoteClassPrompt: true,
            };

            setUserInfo(clientEntry);

            this.handlePreferences(clientEntry).then(result => {
              refreshUserCache(JSON.stringify(clientEntry)).then(res => {
                setUserInfo(clientEntry);
                //setupPreferenceNotifications();
              });
            });
          }
        }
      }
    } catch (error) {
      console.log('An error occurred while fetching client record', error);
    }
  };

  getClientAnniversary(clientId) {
    const soapRequest = new SoapRequest({
      targetNamespace: mbEndpoints.namespace,
      requestURL: mbEndpoints.clientService,
    });

    const xmlRequest = soapRequest.createRequest({
      'ch0:GetClientVisits': {
        'ch0:Request': {
          'ch0:SourceCredentials': {
            'ch0:SourceName': mbApiConfig.credentials.sourceUserName,
            'ch0:Password': mbApiConfig.credentials.sourcePassword,
            'ch0:SiteIDs': {
              'ch0:int': mbApiConfig.credentials.siteId,
            },
          },
          'ch0:XMLDetail': 'Basic',
          'ch0:ClientID': clientId,
          'ch0:StartDate': '2000-01-01',
          'ch0:PageSize': 1,
        },
      },
    });

    return soapRequest.sendRequest(mbEndpoints.getClientsVisitsAction).then(result => {
      let response = result['soap:Envelope']['soap:Body'][0]['GetClientVisitsResponse'][0]['GetClientVisitsResult'][0];

      if (response['Status'][0] === 'Success') {
        if (response['ResultCount'][0] > 0) {
          let firstVisit = response['Visits'][0]['Visit'][0];
          let clientInfo = getUserInfo();
          clientInfo.anniversary = firstVisit['StartDateTime'][0];
          console.log('Anniversary Date', clientInfo.anniversary);
          refreshUserCache(JSON.stringify(clientInfo)).then(res => {
            setUserInfo(clientInfo);
          });
        }
      }
    });
  }

  fetchStaffRecord(userId) {
    const that = this;
    const soapRequest = new SoapRequest({
      targetNamespace: mbEndpoints.namespace,
      requestURL: mbEndpoints.staffService,
    });

    soapRequest.createRequest({
      'ch0:GetStaff': {
        'ch0:Request': {
          'ch0:SourceCredentials': {
            'ch0:SourceName': mbApiConfig.credentials.sourceUserName,
            'ch0:Password': mbApiConfig.credentials.sourcePassword,
            'ch0:SiteIDs': {
              'ch0:int': mbApiConfig.credentials.siteId,
            },
          },
          'ch0:UserCredentials': {
            'ch0:Username': mbApiConfig.credentials.staffUserName,
            'ch0:Password': mbApiConfig.credentials.staffPassword,
            'ch0:SiteIDs': {
              'ch0:int': mbApiConfig.credentials.siteId,
            },
          },
          'ch0:StaffIDs': {
            'ch0:long': userId,
          },
        },
      },
    });

    return soapRequest.sendRequest(mbEndpoints.getStaffAction).then(result => {
      let response = result['soap:Envelope']['soap:Body'][0]['GetStaffResponse'][0]['GetStaffResult'][0];
      if (response['Status'][0] === 'Success') {
        if (response['ResultCount'][0] == 1) {
          let clientEntry = response['StaffMembers'][0]['Staff'][0];

          // Grab the MyZone belt
          clientEntry.myZoneBeltId = null;

          // MyZone belt is in bio field
          if (clientEntry['Bio'] && clientEntry['Bio'].length > 0 && clientEntry['Bio'][0]) {
            let staffBio = clientEntry['Bio'][0];
            if (staffBio.indexOf('[') != -1 && staffBio.indexOf(']') != -1) {
              let start = staffBio.indexOf('[');
              let end = staffBio.indexOf(']');
              clientEntry.myZoneBeltId = staffBio.substring(start + 1, end);
            }
          }

          // Grab the client id, cell phone and image
          clientEntry.userId = parseInt(clientEntry['ID'][0]);
          clientEntry.mobilePhone = clientEntry['MobilePhone'] ? clientEntry['MobilePhone'][0] : '';
          clientEntry.email = clientEntry['Email'] ? clientEntry['Email'][0] : '';
          clientEntry.name = `${clientEntry['FirstName'][0]} ${clientEntry['LastName'][0]}`;
          clientEntry.active = true;
          if (clientEntry['ImageURL'] && clientEntry['ImageURL'].length > 0 && clientEntry['ImageURL'][0]) {
            clientEntry.photoUrl = clientEntry['ImageURL'][0];
          } else {
            clientEntry.photoUrl = null;
          }

          clientEntry.isStaff = true;

          clientEntry.preferences = {
            sessionReminder: false,
            alertsEnabled: true,
            userId: clientEntry.userId,
            remoteClassPrompt: true,
          };

          console.log('handling preferences for staff.');
          this.handlePreferences(clientEntry).then(result => {
            refreshUserCache(JSON.stringify(clientEntry)).then(res => {
              setUserInfo(clientEntry);
            });
          });
        }
      }
    });
  }

  handlePreferences(clientEntry) {
    // Get user preferences
    console.info('clientEntry.userId', clientEntry.userId);
    return this.prefDbRef
      .where('userId', '==', clientEntry.userId)
      .limit(1)
      .get()
      .then(result => {
        if (result.docs.length == 0) {
          this.prefDbRef
            .add(clientEntry.preferences)
            .then(docRef => {
              clientEntry.preferences.recordId = docRef.id;
            })
            .catch(error => {
              console.error('Error adding preferences: ', error);
            });
        } else {
          result.forEach(doc => {
            let {
              alertsEnabled = true,
              sessionReminder = false,
              mealOrderReminder = true,
              chargeMyZoneReminder = true,
              clientLevelTestingReminder = true,
              preferredCalendar = 'default',
              childCarePrompt = true,
              accountabilityPrompt = true,
              remoteClassPrompt = true,
            } = doc.data();
            clientEntry.preferences.alertsEnabled = alertsEnabled;
            clientEntry.preferences.sessionReminder = sessionReminder;
            clientEntry.preferences.mealOrderReminder = mealOrderReminder;
            clientEntry.preferences.chargeMyZoneReminder = chargeMyZoneReminder;
            clientEntry.preferences.clientLevelTestingReminder = clientLevelTestingReminder;
            clientEntry.preferences.preferredCalendar = preferredCalendar;
            clientEntry.preferences.childCarePrompt = childCarePrompt;
            clientEntry.preferences.accountabilityPrompt = accountabilityPrompt;
            clientEntry.preferences.recordId = doc.id;
            clientEntry.preferences.remoteClassPrompt = remoteClassPrompt;
          });
        }
      });
  }

  resetPassword() {
    const { email } = this.state;
    if (this.state.email.trim().length == 0) {
      Alert.alert('Something Went Wrong', 'Please enter your e-mail.', [{ text: 'OK' }], { cancelable: true });
      return;
    }

    this.setState({ loading: true });

    if (this.props.onResetPassword) {
      this.props.onResetPassword(2);
    }

    const soapRequest = new SoapRequest({
      targetNamespace: mbEndpoints.namespace,
      requestURL: mbEndpoints.clientService,
    });

    soapRequest.createRequest({
      'ch0:SendUserNewPassword': {
        'ch0:Request': {
          'ch0:SourceCredentials': {
            'ch0:SourceName': mbApiConfig.credentials.sourceUserName,
            'ch0:Password': mbApiConfig.credentials.sourcePassword,
            'ch0:SiteIDs': {
              'ch0:int': mbApiConfig.credentials.siteId,
            },
          },
          'ch0:UserEmail': email,
        },
      },
    });

    soapRequest.sendRequest(mbEndpoints.resetPasswordAction).then(result => {
      var response =
        result['soap:Envelope']['soap:Body'][0]['SendUserNewPasswordResponse'][0]['SendUserNewPasswordResult'][0];

      if (response['Status'][0] === 'Success') {
        this.setState({
          email: '',
          password: '',
          userId: null,
          loading: false,
          forgotPassword: false,
        });
        Alert.alert('Success', 'A new password has been sent to your e-mail.', [{ text: 'OK' }], { cancelable: true });
      } else {
        this.setState({ loading: false });
        Alert.alert('Something Went Wrong', response['Message'][0], [{ text: 'OK' }], { cancelable: true });
      }
    });
  }

  handleEmail = text => {
    this.setState({ email: text });
  };
  handlePassword = text => {
    this.setState({ password: text });
  };

  render() {
    const { loading, forgotPassword, enrolled, signUp, requiredFields } = this.state;
    let { onResetPassword, onSignUp } = this.props;

    const screenWidth = Dimensions.get('window').width;

    let content = null;

    if (loading) {
      content = <ActivityIndicator size={'large'} color={'white'} style={{ marginBottom: 20 }} />;
    } else {
      if (forgotPassword) {
        content = (
          <View>
            <TextInput
              style={styles.input}
              autoCapitalize="none"
              autoCorrect={false}
              keyboardType="email-address"
              returnKeyType="done"
              placeholder="E-mail"
              placeholderTextColor="rgba(225,225,225,0.7)"
              onChangeText={this.handleEmail}
              value={this.state.email}
            />

            <TouchableOpacity style={styles.loginButtonContainer} onPress={() => this.resetPassword()}>
              <Text style={styles.loginButtonText}>RETRIEVE PASSWORD</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.forgotButtonContainer}
              onPress={() => {
                onResetPassword(0);
                this.setState({
                  email: '',
                  password: '',
                  userId: null,
                  loading: false,
                  forgotPassword: false,
                });
              }}>
              <Text style={styles.forgotButtonText}>Login</Text>
            </TouchableOpacity>
          </View>
        );
      } else if (signUp) {
        let textFields = [];
        if (requiredFields.length > 0) {
          for (let i = 0; i < requiredFields.length; i++) {
            let requiredField = requiredFields[i];
            let keyboardType = 'default';
            let autoCapitalize = 'none';
            let placeholder = requiredField.field.replace(/([a-zA-Z])(?=[A-Z])/g, '$1 ');
            if (placeholder.indexOf('1') != -1) {
              placeholder = placeholder.replace('1', ' 1');
            } else if (placeholder.indexOf('2') != -1) {
              placeholder = placeholder.replace('2', ' 2');
            } else if (placeholder.indexOf('3') != -1) {
              placeholder = placeholder.replace('3', ' 3');
            }

            if (requiredField.field == 'Email') {
              keyboardType = 'email-address';
            } else if (requiredField.field == 'PostalCode') {
              keyboardType = 'number-pad';
            } else if (requiredField.field == 'MobilePhone') {
              keyboardType = 'phone-pad';
            }
            textFields.push(
              <TextInput
                key={`field-${placeholder}`}
                style={styles.input}
                autoCapitalize={autoCapitalize}
                autoCorrect={false}
                keyboardType={keyboardType}
                returnKeyType="done"
                placeholder={placeholder}
                placeholderTextColor="rgba(225,225,225,0.7)"
                onChangeText={text => {
                  requiredField.value = text;
                  this.setState({ requiredFields });
                }}
                value={requiredField.value}
              />,
            );
          }
        }
        content = (
          <View>
            {textFields}
            <TouchableOpacity
              style={[styles.loginButtonContainer]}
              onPress={async () => {
                // Set Progress.
                this.setState({ loading: true });
                let result = await createUserAccount(requiredFields);
                Alert.alert(result.title, result.message, [{ text: 'OK' }], { cancelable: true });
                if (result.success) {
                  onResetPassword(0);
                  this.setState({
                    email: '',
                    password: '',
                    userId: null,
                    loading: false,
                    forgotPassword: false,
                    requiredFields: [],
                    signUp: false,
                  });
                } else {
                  this.setState({ loading: false });
                }
              }}>
              <Text style={styles.loginButtonText}>CREATE ACCOUNT</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.forgotButtonContainer}
              onPress={() => {
                onResetPassword(0);
                this.setState({
                  email: '',
                  password: '',
                  userId: null,
                  loading: false,
                  forgotPassword: false,
                  requiredFields: [],
                  signUp: false,
                });
              }}>
              <Text style={styles.forgotButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        );
      } else {
        let loginBtnContent = (
          <TouchableOpacity style={styles.loginButtonContainer} onPress={() => this.login()}>
            <Text style={styles.loginButtonText}>LOGIN</Text>
          </TouchableOpacity>
        );

        if (enrolled) {
          let image = <Image style={styles.image} source={Assets['faceIdIcon']} resizeMode="contain" />;
          let { enrollmentType } = this.state;
          if (enrollmentType) {
            if (enrollmentType === LocalAuthentication.AuthenticationType.FINGERPRINT) {
              image = <Image style={styles.image} source={Assets['touchIdIcon']} resizeMode="contain" />;
            }
          }
          loginBtnContent = (
            <View style={{ flexDirection: 'row' }}>
              <TouchableOpacity
                style={styles.localAuthButtonContainer1}
                onPress={Platform.OS === 'android' ? this.showAndroidAlert : this.authenticateLocal}>
                {image}
              </TouchableOpacity>
              <TouchableOpacity style={styles.loginButtonContainer1} onPress={() => this.login()}>
                <Text style={styles.loginButtonText}>LOGIN</Text>
              </TouchableOpacity>
            </View>
          );
        }
        content = (
          <View>
            <TextInput
              style={styles.input}
              autoCapitalize="none"
              onSubmitEditing={() => this.passwordInput.focus()}
              autoCorrect={false}
              keyboardType="email-address"
              returnKeyType="next"
              placeholder="E-mail"
              placeholderTextColor="rgba(225,225,225,0.7)"
              onChangeText={this.handleEmail}
              value={this.state.email}
            />

            <TextInput
              style={styles.input}
              returnKeyType="go"
              ref={input => (this.passwordInput = input)}
              placeholder="Password"
              placeholderTextColor="rgba(225,225,225,0.7)"
              secureTextEntry
              onChangeText={this.handlePassword}
              onSubmitEditing={() => this.login()}
              value={this.state.password}
            />

            {loginBtnContent}

            <View
              style={{
                flexDirection: 'row',
                justifyContent: 'space-evenly',
                marginTop: 20,
                marginBottom: 40,
              }}>
              <TouchableOpacity
                style={styles.forgotButton}
                onPress={async () => {
                  let fields = [];
                  let result = await getClientRequiredFields();
                  if (result && result.indexOf('FirstName') == -1) {
                    fields.push({ field: 'FirstName', value: '' });
                  }
                  if (result && result.indexOf('LastName') == -1) {
                    fields.push({ field: 'LastName', value: '' });
                  }
                  if (result && result.length > 0) {
                    for (let i = 0; i < result.length; i++) {
                      fields.push({ field: result[i], value: '' });
                    }
                  }
                  onSignUp();
                  this.setState({ signUp: true, email: '', password: '', requiredFields: fields });
                }}>
                <Text style={[styles.forgotButtonText]}>Sign Up</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.forgotButton}
                onPress={() => {
                  onResetPassword(1);
                  this.setState({ forgotPassword: true, email: '', password: '' });
                }}>
                <Text style={styles.forgotButtonText}>Forgot Password?</Text>
              </TouchableOpacity>
            </View>
          </View>
        );
      }
    }

    let renderContent = (
      <View style={[styles.container]}>
        <StatusBar barStyle={`default`} />
        {content}
      </View>
    );
    if (signUp) {
      renderContent = (
        <ScrollView style={[styles.container]}>
          <StatusBar barStyle={`default`} />
          {content}
        </ScrollView>
      );
    }

    return renderContent;
  }
}

//make this component available to the app
export default withNavigation(LoginForm);