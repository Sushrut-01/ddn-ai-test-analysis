import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

void main() {
  group('NetworkInfo', () {
    // late MockInternetConnectionChecker mockInternetConnectionChecker;
    // late NetworkInfoImpl networkInfo;

    setUp(() {
      // mockInternetConnectionChecker = MockInternetConnectionChecker();
      // networkInfo = NetworkInfoImpl(mockInternetConnectionChecker);
    });

    group('isConnected', () {
      test('should forward the call to InternetConnectionChecker.hasConnection',
          () async {
        // const tHasConnectionFuture = Future.value(true);
        //
        // when(mockInternetConnectionChecker.hasConnection)
        //     .thenAnswer((_) => tHasConnectionFuture);
        //
        // final result = networkInfo.isConnected;
        //
        // verify(mockInternetConnectionChecker.hasConnection);
        // expect(result, tHasConnectionFuture);
      });
    });
  });
}
