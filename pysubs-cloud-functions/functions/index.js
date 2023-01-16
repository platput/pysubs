const functions = require("firebase-functions");

// // Create and deploy your first functions
// // https://firebase.google.com/docs/functions/get-started
// // Ref: https://github.com/firebase/functions-samples

// The Firebase Admin SDK to access Firestore.
const admin = require("firebase-admin");

admin.initializeApp();

exports.addUserToFSOnSignup = functions.auth.user().onCreate(
    (user) => {
      const curDt = new Date();
      const credits = 5;
      const id = user.uid;
      const email = user.email;
      const displayName = user.displayName;
      return admin.firestore().collection("users").doc(id).set({
        id: id,
        email: email,
        displayName: displayName,
        credits: credits,
        createdAt: admin.firestore.Timestamp.fromDate(curDt),
      });
    });

exports.deleteUserFromFSOnAccountDelete = functions.auth.user().onDelete(
    (user) => {
      const id = user.uid;
      const doc = admin.firestore().collection("users").doc(id);
      return doc.delete();
    });
